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
        
        # 🔥 TEST MODE: Always send a notification (even if it's the same order)
        last_order_title = title  # Store last checked order
        full_text = fetch_executive_order_text(link)
        summary = summarize_executive_order(full_text)
        send_notifications(title, link, summary)  # Force notification for testing

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
    send_discord_notification(title, link, summary)

def send_discord_notification(title, link, summary):
    """Sends a Discord notification with the executive order summary."""
    webhook_url = "YOUR_DISCORD_WEBHOOK_URL"  # Replace with your actual webhook URL
    payload = {"content": f"📜 **New Executive Order:** {title}\n🔗 {link}\n\n📌 **Summary:** {summary}"}
    requests.post(webhook_url, json=payload)

# Run the check
check_for_new_executive_orders()
