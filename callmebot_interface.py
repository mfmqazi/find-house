import requests
import urllib.parse

def send_callmebot_message(phone_number, api_key, message):
    """
    Sends a WhatsApp message using the CallMeBot API.
    This provides a simple, HTTP-based interface without browser automation.
    """
    encoded_message = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={encoded_message}&apikey={api_key}"
    
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            print("✅ API Request Sent Successfully.")
            if "Error" in response.text:
                 print(f"⚠️ API Response Warning: {response.text}")
            else:
                 print("Message delivered to WhatsApp!")
        else:
            print(f"❌ API Request Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Network Error: {e}")

if __name__ == "__main__":
    print("--- CallMeBot Test ---")
    # Placeholder values - user needs to provide these
    # PHONE = "1234567890" 
    # API_KEY = "123456" 
    # send_callmebot_message(PHONE, API_KEY, "Test from simple API script")
