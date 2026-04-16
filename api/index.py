import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Config from Vercel Environment Variables
TOKEN = os.environ.get('TELEGRAM_TOKEN')
MY_CHAT_ID = os.environ.get('MY_CHAT_ID')
OBSIDIAN_IP = os.environ.get('OBSIDIAN_IP') 
OBSIDIAN_KEY = os.environ.get('OBSIDIAN_API_KEY')

def send_telegram_msg(chat_id, text):
    """Sends a message back to your Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending to TG: {e}")

@app.route('/api', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return "OK", 200
            
        chat_id = str(data['message']['chat']['id'])
        text = data['message'].get('text', '')

        # 1. SECURITY: Only respond to YOU
        if chat_id != str(MY_CHAT_ID):
            print(f"Unauthorized access attempt from {chat_id}")
            return "OK", 200

        # 2. STATUS CHECK: Type '/status' to test connection
        if text == "/status":
            try:
                headers = {"Authorization": f"Bearer {OBSIDIAN_KEY}"}
                # Pings the root of the Local REST API
                res = requests.get(f"{OBSIDIAN_IP}/", headers=headers, timeout=5)
                if res.status_code == 200:
                    send_telegram_msg(chat_id, "Obsidian: Connected! ✅")
                else:
                    send_telegram_msg(chat_id, f"Obsidian Error: {res.status_code}")
            except Exception as e:
                send_telegram_msg(chat_id, f"Could not reach Mac: {str(e)}")

        # 3. SEARCH VAULT: Any other text is treated as a search
        else:
            try:
                headers = {"Authorization": f"Bearer {OBSIDIAN_KEY}"}
                search_url = f"{OBSIDIAN_IP}/search/"
                # This sends your text to Obsidian's search engine
                res = requests.post(search_url, headers=headers, json={"query": text}, timeout=10)
                
                if res.status_code == 200:
                    results = res.json()
                    if not results:
                        send_telegram_msg(chat_id, f"No notes found for '{text}'")
                    else:
                        # Grabs the first 5 matching filenames
                        titles = [item['filename'] for item in results[:5]]
                        reply = f"🔍 Results for '{text}':\n\n" + "\n".join(titles)
                        send_telegram_msg(chat_id, reply)
                else:
                    send_telegram_msg(chat_id, f"Search error (Code: {res.status_code})")
            except Exception as e:
                send_telegram_msg(chat_id, f"Search failed: {str(e)}")

        return "OK", 200
    except Exception as e:
        print(f"Major Error: {str(e)}")
        return "OK", 200

@app.route('/')
def home():
    return "Obsidian Search Bot is Active!", 200