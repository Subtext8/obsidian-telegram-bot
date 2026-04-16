import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Fetch variables from Vercel Environment Variables
TOKEN = os.environ.get('TELEGRAM_TOKEN')

def send_telegram_msg(chat_id, text):
    """Simple function to send a message back to Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, json=payload, timeout=10)
        # This will help us debug in Vercel Logs if the token is still an issue
        if response.status_code != 200:
            print(f"Telegram API Error: {response.text}")
    except Exception as e:
        print(f"Network Error: {e}")

@app.route('/api', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if data and 'message' in data:
            chat_id = data['message']['chat']['id']
            
            # The bot finally finds its voice!
            send_telegram_msg(chat_id, "Vercel is alive and the folder is fixed! 🚀")
        
        return "OK", 200
    except Exception as e:
        print(f"Internal Error: {str(e)}")
        return "OK", 200 # Keeping it green

@app.route('/')
def home():
    return "The Obsidian Bot is Online!", 200