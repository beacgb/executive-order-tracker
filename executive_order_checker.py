import requests
from bs4 import BeautifulSoup
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# White House Presidential Actions page
URL = "https://www.whitehouse.gov/presidential-actions/"

# Store the last known executive order title
last_order_title = None  

def check_for_new_executive_orders():
    global last_order_title
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    latest_order = soup.find("article")  # Get first article (latest order)
    if latest_order:
        title = latest_order.find("h2").text.strip()
        link = latest_order.find("a")["href"]

        print(f"🔍 Found Executive Order: {title} ({link})")

        # Only send notification if a new executive order is detected
        if title != last_order_title:
            print(f"✅ New Executive Order detected: {title}")
            last_order_title = title  # Update last order
            full_text = fetch_executive_order_text(link)
            summary = summarize_executive_order(full_text)
            send_notifications(title, link, summary)
        else:
            print("⚠️ No new executive orders detected. Skipping notification.")
    else:
        print("⚠️ No executive orders found on the webpage.")


def fetch_executive_order_text(link):
    """Fetches the full text of the executive order from the White House website."""
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    
    content_div = soup.find("div", class_="post-content")  # Adjust selector if needed
    if content_div:
        return content_div.get_text(separator=" ", strip=True)
    return "Full text not available."

def summarize_executive_order(text):
    """Uses Sumy to summarize the executive order text."""
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 3)  # Summarize to 3 sentences
    return " ".join(str(sentence) for sentence in summary)

def send_notifications(title, link, summary):
    """Sends notifications with the executive order summary."""
    print(f"📨 Sending notifications for: {title}")
    send_discord_notification(title, link, summary)
    send_email_notification(title, link, summary)

def send_discord_notification(title, link, summary):
    """Sends a Discord notification with the executive order summary."""
    webhook_url = "https://discord.com/api/webhooks/1336551442294640670/sUIcxlIUHf94JWXSIJ7BNglsVOqMhm3znuCpT-jFRRZgwROKu7zuIVuyNyZqIvNBc4O3"  # Replace with your actual webhook URL
    payload = {"content": f"📜 **New Executive Order:** {title}\n🔗 {link}\n\n📌 **Summary:** {summary}"}
    requests.post(webhook_url, json=payload)

def send_email_notification(title, link, summary):
    """Sends an email notification with the executive order summary."""
    import smtplib
    from email.message import EmailMessage

    sender = "beatricecgomes@gmail.com"
    receiver = "tjandring4@gmail.com"
    password = "pvcy dhwm smzb xwew"  # Use an app password from Google settings

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
        pass
# Run the check
check_for_new_executive_orders()
