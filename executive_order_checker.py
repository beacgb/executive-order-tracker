import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.message import EmailMessage
from transformers import pipeline

# White House Presidential Actions page
URL = "https://www.whitehouse.gov/presidential-actions/"

# Store the last known executive order title
last_order_title = None  

# Load the summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def check_for_new_executive_orders():
    global last_order_title
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    latest_order = soup.find("article")  # Get first article (latest order)
    if latest_order:
        title = latest_order.find("h2").text.strip()
        link = latest_order.find("a")["href"]
        
        if title != last_order_title:  # Only notify if it's new
            last_order_title = title
            full_text = fetch_executive_order_text(link)
            summary = summarize_executive_order(full_text)
            send_notifications(title, link, summary)

def fetch_executive_order_text(link):
    """Fetches the full text of the executive order from the White House website."""
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract text content from the executive order page
    content_div = soup.find("div", class_="post-content")  # Adjust this selector if needed
    if content_div:
        return content_div.get_text(separator=" ", strip=True)
    return "Full text not available."

def summarize_executive_order(text):
    """Uses AI to summarize the executive order text."""
    if len(text) < 500:  # Skip short texts
        return text
    summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def send_notifications(title, link, summary):
    """Sends notifications with the executive order summary."""
    send_email_notification(title, link, summary)
    send_discord_notification(title, link, summary)

def send_email_notification(title, link, summary):
    """Sends an email notification with the executive order summary."""
    sender = "beatricecgomes@gmail.com"
    receiver = "tjandring4@gmail.com"
    password = "pvcy dhwm smzb xwew"  # See Step 4 for setting this up

    subject = "New Executive Order Signed"
    body = f"📜 {title}\n🔗 Read more: {link}\n\n📌 Summary:\n{summary}"

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

def send_discord_notification(title, link, summary):
    """Sends a Discord notification with the executive order summary."""
    webhook_url = "your_discord_webhook_url"  # See Step 5 to set this up
    payload = {"content": f"📜 **New Executive Order:** {title}\n🔗 {link}\n\n📌 **Summary:** {summary}"}
    requests.post(webhook_url, json=payload)

# Run the check every 5 minutes
while True:
    check_for_new_executive_orders()
    time.sleep(300)  # 300 seconds = 5 minutes
