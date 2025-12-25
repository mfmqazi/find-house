import requests
import urllib.parse

def send_textmebot_message(apikey, recipient, message):
    """
    Sends a WhatsApp message using the Text Me Bot API.
    Endpoint: https://api.textmebot.com/send.php
    
    Args:
        apikey (str): Your TextMeBot API Key
        recipient (str): Phone number (international format) OR Group ID (e.g. 120363040377@g.us)
        message (str): The text message to send
    """
    encoded_message = urllib.parse.quote(message)
    url = f"https://api.textmebot.com/send.php?recipient={recipient}&apikey={apikey}&text={encoded_message}"
    
    try:
        response = requests.get(url, timeout=20)
        # TextMeBot usually returns "Success" or similar text
        if response.status_code == 200:
             print("✅ API Request Sent.")
             print(f"Response: {response.text}")
        else:
            print(f"❌ API Request Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Network Error: {e}")

if __name__ == "__main__":
    # Test
    # KEY = "hBBrpaZSe6ke"
    # PHONE = "..." 
    pass
