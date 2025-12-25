import requests

def send_telegram_message(token, chat_id, message):
    """
    Sends a message via Telegram Bot API.
    100% Free, Official API, Reliable.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        # "parse_mode": "Markdown" # Optional
    }
    
    try:
        response = requests.post(url, json=payload, timeout=20)
        data = response.json()
        
        if response.status_code == 200 and data.get("ok"):
            print("✅ Telegram Message SENT.")
        else:
            print(f"❌ Telegram Error: {data.get('description')}")
    except Exception as e:
        print(f"❌ Network Error: {e}")

if __name__ == "__main__":
    print("Test sending...")
    # send_telegram_message("TOKEN", "CHAT_ID", "Hello from House Finder Bot")
