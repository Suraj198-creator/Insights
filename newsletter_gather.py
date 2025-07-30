
from dotenv import load_dotenv
import os
from pprint import pprint
from openai import OpenAI
from prompts import Prompts
from pydantic import BaseModel
# Load environment variables
import anthropic
load_dotenv()

anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))
client = OpenAI(api_key=os.getenv("GPT_KEY"))
# Import your scraper classes
from email_obj import MarketingScraper, AIScraper, SelfHelpScraper, CryptoScraper, Fintech


def claude_prompt(response_data, html_content):
    prompt = f"""I have an HTML email newsletter template and new content that needs to be inserted. I need you to return ONLY the specific HTML sections that need to be updated, not the entire HTML document.

The new content contains:
1. Top 5 marketing stories (main content)
2. Bonus links/additional stories (for the other-links section within the content)

Please:
1. Extract and update ONLY these TWO sections from the provided HTML template:
   - Header section (the div with class "header") - Update the date to today's date
   - Main content section (the div with class "content") - Insert the TOP 5 marketing stories AND the bonus round/additional stories in the other-links subsection

2. For the main content section:
   - Insert the Top 5 marketing stories maintaining the existing HTML structure
   - Each story should use the "newsletter-item" class
   - Convert all article titles into proper hyperlinks using the URLs provided
   - Keep the emoji icons and read-time indicators
   - Maintain the "What's happening?", "Why does it matter?", and "Key Insight:" structure

   - ALSO include the other-links section within the content div:
   - Insert the bonus round/additional marketing stories in the nested "other-links" div
   - Keep the existing structure with the "✨ Other Marketing News Worth a Look" heading
   - Each bonus link should follow the existing format with title, read-time, and description
   - Convert all titles into proper hyperlinks

3. Ensure all links are properly formatted as <a href="URL">Title</a> elements
4. Keep all existing CSS classes and styling structure intact
5. Update the header date to reflect today's date

IMPORTANT: 
- Return ONLY these TWO HTML sections (header and content), not the complete HTML document
- The content section should include BOTH the main newsletter items AND the nested other-links section
- Do not include DOCTYPE, html, head, body tags, or any other surrounding HTML structure
- Make sure to populate BOTH the main newsletter items AND the other-links subsection with the appropriate content from the response

New content to insert: {response_data}

HTML template to extract sections from: {html_content}

Expected output format:
<!-- Header Section -->
<div class="header">
  [updated header content with today's date]
</div>

<!-- Main Content Section (includes both newsletter items and other-links) -->
<div class="content">
  [Top 5 marketing stories in newsletter-item format]

  <!-- Other News Section (nested within content) -->
  <div class="other-links">
    [Bonus round/additional marketing stories]
  </div>
</div>
"""

    return prompt


def merge_html_sections_fixed(original_html, updated_sections):
    """
    Merge the updated sections back into the original HTML template
    This version only handles header and content sections (other-links is nested within content)
    """
    import re

    # Handle None or empty input
    if updated_sections is None:
        print("❌ Updated sections is None!")
        return original_html

    if not isinstance(updated_sections, str):
        print(f"⚠️  Updated sections is not a string, it's {type(updated_sections)}")
        updated_sections = str(updated_sections)

    if len(updated_sections.strip()) == 0:
        print("❌ Updated sections is empty!")
        return original_html

    print("🔍 Analyzing updated sections...")
    print(f"Updated sections length: {len(updated_sections)}")
    print("Updated sections preview:",
          updated_sections[:300] + "..." if len(updated_sections) > 300 else updated_sections)

    # Extract sections from updated content - only look for header and content
    def extract_section_with_proper_nesting(html_content, class_name):
        """Extract a div section by counting opening and closing tags"""
        pattern = f'<div class="{class_name}"[^>]*>'
        start_match = re.search(pattern, html_content)

        if not start_match:
            return None

        start_pos = start_match.start()
        current_pos = start_match.end()
        div_count = 1  # We found the opening div

        while current_pos < len(html_content) and div_count > 0:
            # Look for the next div tag (opening or closing)
            next_div = re.search(r'<(/?)div[^>]*>', html_content[current_pos:])
            if not next_div:
                break

            if next_div.group(1):  # Closing tag
                div_count -= 1
            else:  # Opening tag
                div_count += 1

            current_pos += next_div.end()

        if div_count == 0:
            return html_content[start_pos:current_pos]
        return None

    # Extract sections from updated content - only header and content now
    header_section = extract_section_with_proper_nesting(updated_sections, "header")
    content_section = extract_section_with_proper_nesting(updated_sections, "content")

    print(f"Header section found: {'✓' if header_section else '❌'}")
    print(f"Content section found: {'✓' if content_section else '❌'}")

    if header_section:
        print(f"Header section length: {len(header_section)}")
    if content_section:
        print(f"Content section length: {len(content_section)}")

    result_html = original_html
    changes_made = 0

    # Replace sections in the original HTML
    if header_section:
        try:
            # Extract the original header section
            original_header = extract_section_with_proper_nesting(result_html, "header")
            if original_header:
                result_html = result_html.replace(original_header, header_section)
                changes_made += 1
                print("✓ Header section replaced")
            else:
                print("❌ Could not find original header section")
        except Exception as e:
            print(f"❌ Error replacing header section: {e}")

    if content_section:
        try:
            # Extract the original content section
            original_content = extract_section_with_proper_nesting(result_html, "content")
            if original_content:
                result_html = result_html.replace(original_content, content_section)
                changes_made += 1
                print("✓ Content section replaced (includes nested other-links)")
            else:
                print("❌ Could not find original content section")
        except Exception as e:
            print(f"❌ Error replacing content section: {e}")

    print(f"📊 Total sections replaced: {changes_made}/2")

    if changes_made == 0:
        print("⚠️  No sections were replaced! This might indicate:")
        print("1. Claude didn't return properly formatted HTML sections")
        print("2. The sections are missing from Claude's response")
        print("3. There's a structural mismatch in the HTML")

        # Debug: Let's see what sections we can find in the updated content
        print("\n🔍 Debug: Searching for any div elements in updated sections...")
        div_matches = re.findall(r'<div[^>]*class="([^"]*)"[^>]*>', updated_sections)
        print(f"Found div classes: {div_matches}")

        # Fallback approach - try to use the updated sections as-is if they look complete
        if '<div class="header"' in updated_sections and '<div class="content"' in updated_sections:
            print("🔄 Using fallback: returning Claude's response as-is")
            return updated_sections

    return result_html

# Alternative approach: More direct replacement function
def merge_html_sections_alternative(original_html, updated_sections):
    """
    Alternative approach using string manipulation instead of regex
    """
    if not updated_sections or not isinstance(updated_sections, str):
        return original_html

    print("🔄 Using alternative merge approach...")

    # Find the boundaries of each section in the original HTML
    sections_to_replace = ["header", "content", "other-links"]
    result_html = original_html

    for section_class in sections_to_replace:
        # Find the section in updated content
        start_pattern = f'<div class="{section_class}"'
        start_idx = updated_sections.find(start_pattern)

        if start_idx == -1:
            print(f"❌ {section_class} section not found in updated content")
            continue

        # Find the end of this div by counting tags
        current_pos = start_idx
        div_count = 0
        in_tag = False
        section_start = start_idx

        while current_pos < len(updated_sections):
            char = updated_sections[current_pos]

            if char == '<':
                in_tag = True
                # Check if this is a div tag
                remaining = updated_sections[current_pos:]
                if remaining.startswith('<div'):
                    div_count += 1
                elif remaining.startswith('</div>'):
                    div_count -= 1
                    if div_count == 0:
                        # Found the end of our section
                        end_pos = current_pos + remaining.find('>') + 1
                        new_section = updated_sections[section_start:end_pos]

                        # Now replace in original HTML
                        orig_start = result_html.find(f'<div class="{section_class}"')
                        if orig_start != -1:
                            # Find the end of the original section
                            orig_pos = orig_start
                            orig_div_count = 0

                            while orig_pos < len(result_html):
                                if result_html[orig_pos:].startswith('<div'):
                                    orig_div_count += 1
                                elif result_html[orig_pos:].startswith('</div>'):
                                    orig_div_count -= 1
                                    if orig_div_count == 0:
                                        orig_end = orig_pos + result_html[orig_pos:].find('>') + 1
                                        # Replace the section
                                        result_html = (result_html[:orig_start] +
                                                       new_section +
                                                       result_html[orig_end:])
                                        print(f"✓ {section_class} section replaced successfully")
                                        break
                                orig_pos += 1
                        break
            elif char == '>' and in_tag:
                in_tag = False

            current_pos += 1

    return result_html


def generate_marketing_newsletter():
    print("\n=== Marketing Newsletter Generation ===")
    try:
        marketing = MarketingScraper()
        marketing_results = marketing.scrape_all()
        print("Scraped Articles:")
        pprint(marketing_results)

    except Exception as e:
        print(f"Error scraping marketing data: {e}")
        return None

    # Read the original template
    try:
        with open("templates/Marketing_news.html", encoding="utf-8") as file:
            html_content = file.read()
        print(f"✓ Successfully read HTML template ({len(html_content)} characters)")
    except Exception as e:
        print(f"❌ Error reading HTML template: {e}")
        return None

    prompt_obj = Prompts(marketing_results)
    prompt = prompt_obj.marketing_prompt()

    # Get content from OpenAI
    try:
        response = client.responses.create(
            model="o4-mini",
            reasoning={"effort": "high"},
            input=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        response_data = response.output_text
        print(f"✓ OpenAI Response received ({len(response_data)} characters)")
        print("OpenAI Response preview:", response_data[:200] + "..." if len(response_data) > 200 else response_data)
    except Exception as e:
        print(f"❌ Error getting OpenAI response: {e}")
        return None

    # Get updated sections from Claude using the FIXED prompt
    try:
        claude_prompt_text = claude_prompt(response_data, html_content)  # This now uses the fixed version
        print(f"✓ Claude prompt prepared ({len(claude_prompt_text)} characters)")

        anthro_response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=5000,
            messages=[
                {"role": "user", "content": claude_prompt_text}
            ]
        )

        print(f"✓ Claude response received")

        # Handle Claude response (same as before)
        updated_sections = None
        if hasattr(anthro_response, 'content'):
            if isinstance(anthro_response.content, list):
                text_blocks = []
                for i, block in enumerate(anthro_response.content):
                    if hasattr(block, 'text'):
                        text_blocks.append(block.text)
                    elif hasattr(block, 'content'):
                        text_blocks.append(str(block.content))
                    else:
                        text_blocks.append(str(block))
                updated_sections = ''.join(text_blocks)
            elif isinstance(anthro_response.content, str):
                updated_sections = anthro_response.content
            else:
                updated_sections = str(anthro_response.content)

        if updated_sections is None or updated_sections == "":
            print("❌ Failed to extract content from Claude response!")
            return None

        print(f"✓ Combined sections length: {len(updated_sections)} characters")

    except Exception as e:
        print(f"❌ Error getting Claude response: {e}")
        import traceback
        traceback.print_exc()
        return None

        # Parse the updated sections and merge them back into the original template
    try:
        updated_html = merge_html_sections_fixed(html_content, updated_sections)
        print(f"✓ HTML sections merged successfully ({len(updated_html)} characters)")

        # Check if any changes were made
        if updated_html == html_content:
            print("⚠️  Warning: No changes detected in HTML after merge!")

    except Exception as e:
        print(f"❌ Error merging HTML sections: {e}")
        import traceback
        traceback.print_exc()
        return None

        # Write the complete updated HTML back to file
    try:
        with open("templates/Marketing_news.html", "w", encoding="utf-8") as file:
            file.write(updated_html)
        print("✓ Successfully wrote updated AI HTML to file")

        # Verify the file was written
        with open("templates/Marketing_news.html", "r", encoding="utf-8") as file:
            verification_content = file.read()
        print(f"✓ File verification: {len(verification_content)} characters written")

    except Exception as e:
        print(f"❌ Error writing AI HTML file: {e}")
        return None

    return True

def generate_AI_newsletter():
    print("\n=== AI Newsletter Generation ===")
    try:
        ai = AIScraper()
        ai_results = ai.scrape_all()
        print("Scraped Articles:")
        pprint(ai_results)
    except Exception as e:
        print(f"Error scraping AI data: {e}")
        return None

    # Read the original template (assuming you have an AI template, or copy from marketing)
    try:
        # You'll need to create an AI_news.html template or copy from Marketing_news.html
        with open("templates/ai_news.html", encoding="utf-8") as file:
            html_content = file.read()
        print(f"✓ Successfully read AI HTML template ({len(html_content)} characters)")
    except Exception as e:
        print(f"❌ Error reading AI HTML template: {e}")
        # Fallback to marketing template if AI template doesn't exist
        try:
            with open("templates/Marketing_news.html", encoding="utf-8") as file:
                html_content = file.read()
            print(f"✓ Using marketing template as fallback ({len(html_content)} characters)")
        except Exception as e2:
            print(f"❌ Error reading fallback template: {e2}")
            return None

    # Create prompt using the AI prompt method
    prompt_obj = Prompts(ai_results)
    prompt = prompt_obj.AI_prompt()

    # Get content from OpenAI
    try:
        response = client.responses.create(
            model="o4-mini",
            reasoning={"effort": "high"},
            input=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        response_data = response.output_text
        print(f"✓ OpenAI Response received ({len(response_data)} characters)")
        print("OpenAI Response preview:", response_data[:200] + "..." if len(response_data) > 200 else response_data)
    except Exception as e:
        print(f"❌ Error getting OpenAI response: {e}")
        return None

    # Get updated sections from Claude using the AI-specific prompt
    try:
        claude_prompt_text = claude_prompt(response_data, html_content)
        print(f"✓ Claude AI prompt prepared ({len(claude_prompt_text)} characters)")

        anthro_response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=5000,
            messages=[
                {"role": "user", "content": claude_prompt_text}
            ]
        )

        print(f"✓ Claude response received")

        # Handle Claude response (same pattern as marketing newsletter)
        updated_sections = None
        if hasattr(anthro_response, 'content'):
            if isinstance(anthro_response.content, list):
                text_blocks = []
                for i, block in enumerate(anthro_response.content):
                    if hasattr(block, 'text'):
                        text_blocks.append(block.text)
                    elif hasattr(block, 'content'):
                        text_blocks.append(str(block.content))
                    else:
                        text_blocks.append(str(block))
                updated_sections = ''.join(text_blocks)
            elif isinstance(anthro_response.content, str):
                updated_sections = anthro_response.content
            else:
                updated_sections = str(anthro_response.content)

        if updated_sections is None or updated_sections == "":
            print("❌ Failed to extract content from Claude response!")
            return None

        print(f"✓ Combined sections length: {len(updated_sections)} characters")

    except Exception as e:
        print(f"❌ Error getting Claude response: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Parse the updated sections and merge them back into the original template
    try:
        updated_html = merge_html_sections_fixed(html_content, updated_sections)
        print(f"✓ HTML sections merged successfully ({len(updated_html)} characters)")

        # Check if any changes were made
        if updated_html == html_content:
            print("⚠️  Warning: No changes detected in HTML after merge!")

    except Exception as e:
        print(f"❌ Error merging HTML sections: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Write the complete updated HTML back to file
    try:
        with open("templates/AI_news.html", "w", encoding="utf-8") as file:
            file.write(updated_html)
        print("✓ Successfully wrote updated AI HTML to file")

        # Verify the file was written
        with open("templates/AI_news.html", "r", encoding="utf-8") as file:
            verification_content = file.read()
        print(f"✓ File verification: {len(verification_content)} characters written")

    except Exception as e:
        print(f"❌ Error writing AI HTML file: {e}")
        return None

    return True

def generate_fintech_newsletter():
    """Main function to generate the fintech newsletter"""

    # --- 1. Scrape the initial data ---
    print("\n=== Fintech Newsletter Generation ===")
    try:
        fintech = Fintech()
        fintech_results = fintech.scrape_all()
        print("Scraped Articles:")
        pprint(fintech_results)
    except Exception as e:
        print(f"Error scraping Fintech data: {e}")
        return None

    # Read the original template (assuming you have an Fintech template, or copy from marketing)
    try:
        # You'll need to create an Fintech.html template or copy from Marketing_news.html
        with open("templates/fintech.html", encoding="utf-8") as file:
            html_content = file.read()
        print(f"✓ Successfully read Fintech HTML template ({len(html_content)} characters)")
    except Exception as e:
        print(f"❌ Error reading Fintech HTML template: {e}")
        # Fallback to marketing template if Fintech template doesn't exist
        try:
            with open("templates/fintech.html", encoding="utf-8") as file:
                html_content = file.read()
            print(f"✓ Using marketing template as fallback ({len(html_content)} characters)")
        except Exception as e2:
            print(f"❌ Error reading fallback template: {e2}")
            return None

    # Create prompt using the Fintech prompt method
    prompt_obj = Prompts(fintech_results)
    prompt = prompt_obj.Fintech_prompt()

    # Get content from OpenAI
    try:
        response = client.responses.create(
            model="o4-mini",
            reasoning={"effort": "high"},
            input=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        response_data = response.output_text
        print(f"✓ OpenAI Response received ({len(response_data)} characters)")
        print("OpenAI Response preview:", response_data[:200] + "..." if len(response_data) > 200 else response_data)
    except Exception as e:
        print(f"❌ Error getting OpenAI response: {e}")
        return None

    # Get updated sections from Claude using the AI-specific prompt
    try:
        claude_prompt_text = claude_prompt(response_data, html_content)
        print(f"✓ Claude AI prompt prepared ({len(claude_prompt_text)} characters)")

        anthro_response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=5000,
            messages=[
                {"role": "user", "content": claude_prompt_text}
            ]
        )

        print(f"✓ Claude response received")

        # Handle Claude response (same pattern as marketing newsletter)
        updated_sections = None
        if hasattr(anthro_response, 'content'):
            if isinstance(anthro_response.content, list):
                text_blocks = []
                for i, block in enumerate(anthro_response.content):
                    if hasattr(block, 'text'):
                        text_blocks.append(block.text)
                    elif hasattr(block, 'content'):
                        text_blocks.append(str(block.content))
                    else:
                        text_blocks.append(str(block))
                updated_sections = ''.join(text_blocks)
            elif isinstance(anthro_response.content, str):
                updated_sections = anthro_response.content
            else:
                updated_sections = str(anthro_response.content)

        if updated_sections is None or updated_sections == "":
            print("❌ Failed to extract content from Claude response!")
            return None

        print(f"✓ Combined sections length: {len(updated_sections)} characters")

    except Exception as e:
        print(f"❌ Error getting Claude response: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Parse the updated sections and merge them back into the original template
    try:
        updated_html = merge_html_sections_fixed(html_content, updated_sections)
        print(f"✓ HTML sections merged successfully ({len(updated_html)} characters)")

        # Check if any changes were made
        if updated_html == html_content:
            print("⚠️  Warning: No changes detected in HTML after merge!")

    except Exception as e:
        print(f"❌ Error merging HTML sections: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Write the complete updated HTML back to file
    try:
        with open("templates/fintech.html", "w", encoding="utf-8") as file:
            file.write(updated_html)
        print("✓ Successfully wrote updated Fintech HTML to file")

        # Verify the file was written
        with open("templates/fintech.html", "r", encoding="utf-8") as file:
            verification_content = file.read()
        print(f"✓ File verification: {len(verification_content)} characters written")

    except Exception as e:
        print(f"❌ Error writing Fintech HTML file: {e}")
        return None

    return True


def generate_crypto_newsletter():
    """Main function to generate the crypto newsletter"""

    # --- 1. Scrape the initial data ---
    print("\n=== Crypto Newsletter Generation ===")
    try:
        crypto = CryptoScraper()
        crypto_results = crypto.scrape_all()
        print("Scraped Articles:")
        pprint(crypto_results)
    except Exception as e:
        print(f"Error scraping crypto data: {e}")
        return None

    # Read the original template (assuming you have an Crypto template, or copy from marketing)
    try:
        # You'll need to create an crypto_news.html template or copy from Marketing_news.html
        with open("templates/crypto_news.html", encoding="utf-8") as file:
            html_content = file.read()
        print(f"✓ Successfully read crypto HTML template ({len(html_content)} characters)")
    except Exception as e:
        print(f"❌ Error reading crypto HTML template: {e}")
        # Fallback to marketing template if Crypto template doesn't exist
        try:
            with open("templates/crypto_news.html", encoding="utf-8") as file:
                html_content = file.read()
            print(f"✓ Using marketing template as fallback ({len(html_content)} characters)")
        except Exception as e2:
            print(f"❌ Error reading fallback template: {e2}")
            return None

    # Create prompt using the Crypto prompt method
    prompt_obj = Prompts(crypto_results)
    prompt = prompt_obj.crypto_prompt()

    # Get content from OpenAI
    try:
        response = client.responses.create(
            model="o4-mini",
            reasoning={"effort": "high"},
            input=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        response_data = response.output_text
        print(f"✓ OpenAI Response received ({len(response_data)} characters)")
        print("OpenAI Response preview:", response_data[:200] + "..." if len(response_data) > 200 else response_data)
    except Exception as e:
        print(f"❌ Error getting OpenAI response: {e}")
        return None

    # Get updated sections from Claude using the AI-specific prompt
    try:
        claude_prompt_text = claude_prompt(response_data, html_content)
        print(f"✓ Claude AI prompt prepared ({len(claude_prompt_text)} characters)")

        anthro_response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=5000,
            messages=[
                {"role": "user", "content": claude_prompt_text}
            ]
        )

        print(f"✓ Claude response received")

        # Handle Claude response (same pattern as marketing newsletter)
        updated_sections = None
        if hasattr(anthro_response, 'content'):
            if isinstance(anthro_response.content, list):
                text_blocks = []
                for i, block in enumerate(anthro_response.content):
                    if hasattr(block, 'text'):
                        text_blocks.append(block.text)
                    elif hasattr(block, 'content'):
                        text_blocks.append(str(block.content))
                    else:
                        text_blocks.append(str(block))
                updated_sections = ''.join(text_blocks)
            elif isinstance(anthro_response.content, str):
                updated_sections = anthro_response.content
            else:
                updated_sections = str(anthro_response.content)

        if updated_sections is None or updated_sections == "":
            print("❌ Failed to extract content from Claude response!")
            return None

        print(f"✓ Combined sections length: {len(updated_sections)} characters")

    except Exception as e:
        print(f"❌ Error getting Claude response: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Parse the updated sections and merge them back into the original template
    try:
        updated_html = merge_html_sections_fixed(html_content, updated_sections)
        print(f"✓ HTML sections merged successfully ({len(updated_html)} characters)")

        # Check if any changes were made
        if updated_html == html_content:
            print("⚠️  Warning: No changes detected in HTML after merge!")

    except Exception as e:
        print(f"❌ Error merging HTML sections: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Write the complete updated HTML back to file
    try:
        with open("templates/crypto_news.html", "w", encoding="utf-8") as file:
            file.write(updated_html)
        print("✓ Successfully wrote updated Crypto HTML to file")

        # Verify the file was written
        with open("templates/crypto_news.html", "r", encoding="utf-8") as file:
            verification_content = file.read()
        print(f"✓ File verification: {len(verification_content)} characters written")

    except Exception as e:
        print(f"❌ Error writing Crypto HTML file: {e}")
        return None

    return True





def main():
    """Main entry point - choose what to run"""

    # Uncomment this line if you want to test other scrapers first
    # test_other_scrapers()

    # Generate the fintech newsletter
    newsletter_data = generate_marketing_newsletter()


if __name__ == "__main__":
    main()