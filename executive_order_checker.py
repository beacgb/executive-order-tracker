import requests
import os
from bs4 import BeautifulSoup
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

# White House Presidential Actions page
URL = "https://www.whitehouse.gov/presidential-actions/"

# Store the last known executive order title
last_order_title = None  

def check_for_new_executive_orders():
    # File to store the last known executive order title
    LAST_TITLE_FILE = "last_executive_order.txt"

    # Read the last stored title (if it exists)
    last_order_title = None
    if os.path.exists(LAST_TITLE_FILE):
        with open(LAST_TITLE_FILE, "r") as file:
            last_order_title = file.read().strip()

    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the latest executive order
    latest_order = soup.find("li", class_="wp-block-post")
    if latest_order:
        title_tag = latest_order.find("h2", class_="wp-block-post-title has-heading-4-font-size")
        link_tag = title_tag.find("a") if title_tag else None

        if title_tag and link_tag:
            title = title_tag.text.strip()
            link = link_tag["href"]

            # Only send notification if a new executive order is detected
            if title != last_order_title:
                print(f"✅ New Executive Order detected: {title}")
                
                # Update the stored title
                with open(LAST_TITLE_FILE, "w") as file:
                    file.write(title)

                # Fetch and summarize the text
                full_text = fetch_executive_order_text(link)
                summary = summarize_executive_order(full_text)
                send_notifications(title, link, summary)
            else:
                print("⚠️ No new executive orders detected. Skipping notification.")
    else:
        print("⚠️ No executive orders found on the webpage.")

def fetch_executive_order_text(link):
    """Fetches and extracts the full text of an executive order from the White House website."""
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    # Locate the main article content
    content_div = soup.find("div", class_="wp-block-post-content")
    if not content_div:
        content_div = soup.find("div", class_="entry-content")  # Alternative selector

    if content_div:
        paragraphs = content_div.find_all("p")  # Extract all paragraphs
        extracted_text = []

        for p in paragraphs:
            text = p.get_text(strip=True)
            extracted_text.append(text)

        # Join paragraphs into a full document text
        full_text = "\n".join(extracted_text)
        
        # Ensure text is long enough for summarization
        if len(full_text.split()) < 50:  # If too short, return full text instead
            return full_text
        
        return full_text

    return "Full text not available."

def summarize_executive_order(text, num_sentences=3):
    """Generates a summary with a sentence count limited between 1 and 6."""
    num_sentences = max(1, min(num_sentences, 6))  # Ensure sentence count is between 1 and 6
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = TextRankSummarizer()  # Use TextRank for improved coherence
    summary = summarizer(parser.document, num_sentences)

    # Join the summarized sentences into a paragraph
    return " ".join(str(sentence) for sentence in summary)

def send_notifications(title, link, summary):
    """Sends notifications with the executive order summary."""
    send_discord_notification(title, link, summary)
    send_email_notification(title, link, summary)  # Optional: Uncomment if using email

def send_discord_notification(title, link, summary):
    """Sends a Discord notification with the executive order summary."""
    webhook_url = "https://discord.com/api/webhooks/1336551442294640670/sUIcxlIUHf94JWXSIJ7BNglsVOqMhm3znuCpT-jFRRZgwROKu7zuIVuyNyZqIvNBc4O3"  # Replace with your actual webhook URL
    payload = {"content": f"📜 **New Executive Order:** {title}\n🔗 {link}\n\n📌 **Summary:** {summary}"}
    response = requests.post(webhook_url, json=payload)

def send_email_notification(title, link, summary):
    """Sends an email notification with the executive order summary."""
    import smtplib
    from email.message import EmailMessage

    sender = "beatricecgomes@gmail.com"
    receiver = "tjandring4@gmail.com"
    password = "pvcydhwmsmzbxwew"  # Use an app password from Google settings

    subject = "New Executive Order Signed"
    body = f"📜 {title}\n🔗 Read more: {link}\n\n📌 Summary:\n{summary}"

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
    except Exception:
        pass  # Suppress errors to keep the script silent

# Run the check
check_for_new_executive_orders()
