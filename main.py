
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from flask import Flask, request, redirect, url_for, render_template, jsonify, session

from datetime import datetime
load_dotenv()
urls=["https://techcrunch.com/feed/","https://www.theverge.com/rss/index.xml", "https://www.wired.com/feed/rss", "https://hnrss.org/frontpage"]


url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session storage

@app.route('/')
def index():
    return render_template('test2.html')
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
            insert_resp = supabase.table("emails").insert({
                "email": email,
                "created_at": datetime.now().isoformat()
            }).execute()
            email_id = insert_resp.data[0]["id"]
            print("email has been updated in supabase")

        # Step 2: Insert subscriptions
        for slug in selections:
            try:
                print(f"Processing slug: {slug}")
                nl_resp = supabase.table("newsletters").select("id").eq("slug", slug).execute()
                print(nl_resp)

                if not nl_resp.data:
                    print("skipping invalid slug")
                    continue  # skip invalid slugs
                newsletter_id = nl_resp.data[0]["id"]

                supabase.table("subscriptions").upsert({
                    "email_id": email_id,
                    "newsletter_id": newsletter_id,
                    "status": "subscribed",
                    "subscribed_at": datetime.now().isoformat()
                }).execute()
                print("subscriptions updated")
            except Exception as e:
                print("error:", e)


        return jsonify({'redirect': url_for('confirmation')})

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Server error'}), 500

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')




if __name__ == "__main__":
    app.run(debug=True)