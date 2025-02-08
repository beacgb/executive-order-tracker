import requests
import os
import smtplib
from bs4 import BeautifulSoup
from email.message import EmailMessage

# White House Presidential Actions page
URL = "https://www.whitehouse.gov/presidential-actions/"

# Discord Webhook URL
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# Email Configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def get_latest_executive_order():
    """Fetches the latest executive order details from the White House website."""
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    latest_order = soup.find("li", class_="wp-block-post")
    if latest_order:
        title_tag = latest_order.find("h2", class_="wp-block-post-title has-heading-4-font-size")
        link_tag = title_tag.find("a") if title_tag else None

        if title_tag and link_tag:
            return title_tag.text.strip(), link_tag["href"]

    return None, None

def fetch_executive_order_text(link):
    """Fetches the full text of the executive order."""
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    content_div = soup.find("div", class_="wp-block-post-content") or soup.find("div", class_="entry-content")
    if content_div:
        paragraphs = content_div.find_all("p")
        full_text = "\n".join(p.get_text(strip=True) for p in paragraphs)
        return full_text if len(full_text.split()) > 50 else "Full text not available."
    return "Full text not available."

def summarize_executive_order(text):
    """Uses ChatGPT to generate a concise third-person summary."""
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [{"role": "system", "content": "Summarize the following executive order in a third-person paragraph:"},
                     {"role": "user", "content": text}]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"].strip()

def send_discord_notification(title, link, summary):
    """Sends a notification to Discord."""
    payload = {"content": f"📜 **New Executive Order:** {title}\n🔗 {link}\n\n📌 **Summary:** {summary}"}
    requests.post(DISCORD_WEBHOOK, json=payload)

def send_email_notification(title, link, summary):
    """Sends an email notification with the executive order summary."""
    msg = EmailMessage()
    msg.set_content(f"📜 {title}\n🔗 {link}\n\n📌 Summary:\n{summary}")
    msg["Subject"] = "New Executive Order Signed"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

def main():
    """Main execution function."""
    title, link = get_latest_executive_order()
    
    if title and link:
        full_text = fetch_executive_order_text(link)
        summary = summarize_executive_order(full_text)
        
        # Send notifications
        send_discord_notification(title, link, summary)
        send_email_notification(title, link, summary)

if __name__ == "__main__":
    main()
