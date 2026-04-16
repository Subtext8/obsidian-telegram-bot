import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Constants from your setup
TAILSCALE_URL = "http://100.70.72.81:27123"
OBSIDIAN_KEY = os.getenv("OBSIDIAN_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_CHAT_ID = os.getenv("MY_CHAT_ID")

def send_telegram_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route('/api', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data or 'message' not in data:
        return "OK", 200

    chat_id = str(data['message']['chat']['id'])
    text = data['message'].get('text', '')

    # 1. Security Check
    if chat_id != MY_CHAT_ID:
        return "Unauthorized", 403

    # 2. Process Commands
    if text.lower() == "/status":
        try:
            r = requests.get(f"{TAILSCALE_URL}/status", timeout=5)
            status = "Connected! ✅" if r.status_code == 200 else "Mac is offline. ❌"
        except:
            status = "Tunnel closed. ❌"
        send_telegram_msg(chat_id, status)

    # 3. Simple Search Logic
    else:
        send_telegram_msg(chat_id, f"Searching for: {text}...")
        headers = {"Authorization": f"Bearer {OBSIDIAN_KEY}"}
        # We use the 'simple search' endpoint we discussed
        search_url = f"{TAILSCALE_URL}/search/simple/?query={text}"
        
        try:
            r = requests.post(search_url, headers=headers, timeout=10)
            results = r.json()
            if results:
                # Show the top 5 matches
                files = "\n".join([f"📄 {res['filename']}" for res in results[:5]])
                send_telegram_msg(chat_id, f"Found these:\n{files}")
            else:
                send_telegram_msg(chat_id, "No matches found in your vault.")
        except Exception as e:
            send_telegram_msg(chat_id, f"Error reaching Mac: {str(e)}")

    return "OK", 200