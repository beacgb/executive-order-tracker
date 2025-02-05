import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
from transformers import pipeline

# White House Presidential Actions page
URL = "https://www.whitehouse.gov/presidential-actions/"

def check_for_new_executive_orders():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    
    latest_order = soup.find("article")  # Get first article (latest order)
    if latest_order:
        title = latest_order.find("h2").text.strip()
        link = latest_order.find("a")["href"]
        return title, link
    return None, None

def send_email_notification(title, link):
    sender = "beatricecgomes@gmail.com"
    receiver = "tjandring4@gmail.com"
    password = "pvcy dhwm smzb xwew"  # See Step 4 to get this

    subject = "New Executive Order Signed"
    body = f"New Executive Order: {title}\nRead more: {link}"

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

def send_discord_notification(title, link):
    webhook_url = "your_discord_webhook_url"  # See Step 5 to set this up
    payload = {"content": f"📜 New Executive Order: {title}\n🔗 {link}"}
    requests.post(webhook_url, json=payload)


def summarize_executive_order(text):
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=250, min_length=30, do_sample=False)
    return summary[0]['summary_text']

# Check for new executive orders
title, link = check_for_new_executive_orders()

if title:
    print(f"New Executive Order: {title}\nRead more: {link}")
    
    # Send notifications
    send_email_notification(title, link)
    send_discord_notification(title, link)
