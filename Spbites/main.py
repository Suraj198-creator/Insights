import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from flask import Flask, request, redirect, url_for, render_template, jsonify, session
import secrets
from datetime import datetime

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session storage


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/update', methods=['POST'])
def update_database():
    email = request.form['email']
    session['email'] = email  # Temporarily store in session
    return render_template("checklist2.html")


@app.route('/submit-newsletters', methods=['POST'])
def submit_newsletters():
    try:
        data = request.get_json()
        selections = data.get('selections', [])
        print(selections)
        email = session.get('email')

        if not email:
            return jsonify({'error': 'Session expired or missing email'}), 400

        # Step 1: Get or insert email
        email_resp = supabase.table("emails").select("id").eq("email", email).execute()
        if email_resp.data:
            email_id = email_resp.data[0]["id"]
        else:
            unsubscribe_token = secrets.token_urlsafe(16)
            insert_resp = supabase.table("emails").upsert({
                "email": email,
                "created_at": datetime.now().isoformat(),
                "unsubscribe_token": unsubscribe_token
            }).execute()
            email_id = insert_resp.data[0]["id"]
            print("email has been updated in supabase")

            # Check if email already exists and add token if missing
            if email_resp.data:
                email_data = email_resp.data[0]
                email_id = email_data["id"]
                if not email_data.get("unsubscribe_token"):
                    unsubscribe_token = secrets.token_urlsafe(16)
                    supabase.table("emails").update({"unsubscribe_token": unsubscribe_token}).eq("id",
                                                                                                 email_id).execute()

        # Step 2: Insert/Update subscriptions (FIXED FOR RESUBSCRIPTION)
        for slug in selections:
            try:
                print(f"Processing slug: {slug}")
                nl_resp = supabase.table("newsletters").select("id").eq("slug", slug).execute()
                print(nl_resp)

                if not nl_resp.data:
                    print("skipping invalid slug")
                    continue  # skip invalid slugs
                newsletter_id = nl_resp.data[0]["id"]

                # Check if subscription already exists
                existing_sub = supabase.table("subscriptions").select("id", "status").eq("email_id", email_id).eq(
                    "newsletter_id", newsletter_id).execute()

                if existing_sub.data:
                    # Subscription exists - update it to subscribed status
                    supabase.table("subscriptions").update({
                        "status": "subscribed",
                        "subscribed_at": datetime.now().isoformat(),
                        "unsubscribed_at": None,  # Clear unsubscribe timestamp
                        "unsub_reason": None,  # Clear unsubscribe reason
                        "additional_feedback": None  # Clear feedback
                    }).eq("email_id", email_id).eq("newsletter_id", newsletter_id).execute()
                    print(f"Re-subscribed user to newsletter {slug}")
                else:
                    # New subscription - insert it
                    supabase.table("subscriptions").insert({
                        "email_id": email_id,
                        "newsletter_id": newsletter_id,
                        "status": "subscribed",
                        "subscribed_at": datetime.now().isoformat()
                    }).execute()
                    print(f"New subscription created for newsletter {slug}")

            except Exception as e:
                print("error:", e)

        return jsonify({'redirect': url_for('confirmation')})

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Server error'}), 500


@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

# @app.route("/preview-newsletter")
# def preview_newsletter():
#     email = "someone@example.com"
#     token = "abc123"
#     slug = "ai"
#     unsubscribe_link = f"https://yourdomain.com/unsubscribe/{slug}?token={token}"
#
#     html = render_template("ai_news.html", unsubscribe_link=unsubscribe_link)
#     return html

@app.route('/unsubscribe/<slug>', methods=['GET', 'POST'])
def unsubscribe(slug):
    token = request.args.get("token")
    if not token:
        return "Missing token", 400

    # Step 1: Look up the user by token
    email_resp = supabase.table("emails").select("id", "email").eq("unsubscribe_token", token).execute()
    if not email_resp.data:
        return "Invalid or expired token", 404

    email_data = email_resp.data[0]
    email_id = email_data["id"]
    email = email_data["email"]

    # Step 2: Look up the newsletter by slug
    nl_resp = supabase.table("newsletters").select("id").eq("slug", slug).execute()
    if not nl_resp.data:
        return "Invalid newsletter slug", 404

    newsletter_data = nl_resp.data[0]
    newsletter_id = newsletter_data["id"]

    if request.method == 'POST':
        submitted_email = request.form.get("email")
        print(f"Submitted email: {submitted_email}")

        # Check if email matches (case insensitive)
        if submitted_email.lower() != email.lower():
            # Return JSON error response for AJAX
            if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
                return jsonify({'error': 'EMAIL_MISMATCH', 'message': "Email confirmation doesn't match."}), 403
            else:
                return "Email confirmation doesn't match.", 403

        # Step 3: Process unsubscribe reasons and feedback
        unsubscribe_reasons = request.form.get("unsubscribe_reasons")
        additional_feedback = request.form.get("additional_feedback")

        # Parse the JSON string of reasons if it exists
        reasons_list = []
        if unsubscribe_reasons:
            try:
                reasons_list = json.loads(unsubscribe_reasons)
                print(f"Unsubscribe reasons: {reasons_list}")
            except json.JSONDecodeError:
                print("Error parsing unsubscribe reasons JSON")
                reasons_list = []

        # Step 4: Update the subscription status to unsubscribed
        try:
            supabase.table("subscriptions").update({
                "status": "unsubscribed",
                "unsubscribed_at": datetime.now().isoformat(),
                "unsub_reason": reasons_list,  # Store as JSONB array
                "additional_feedback": additional_feedback if additional_feedback else None
            }).eq("email_id", email_id).eq("newsletter_id", newsletter_id).execute()

            print(f"User {email} unsubscribed from newsletter {slug}")
            if reasons_list:
                print(f"Reasons: {', '.join(reasons_list)}")
            if additional_feedback:
                print(f"Additional feedback: {additional_feedback}")

            # Return success response
            return jsonify({'success': True, 'message': 'Successfully unsubscribed'}), 200

        except Exception as e:
            print(f"Database error: {e}")
            return jsonify(
                {'error': 'SERVER_ERROR', 'message': 'An error occurred while processing your request.'}), 500

    # On GET, show the unsubscribe form
    return render_template("unsubscribed.html", email=email, slug=slug, token=token, unsubscribed=False)

if __name__ == "__main__":
    app.run(debug=True)