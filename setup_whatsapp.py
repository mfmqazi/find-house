from textmebot_interface import send_textmebot_message
import time

# API Key provided by user
API_KEY = "hBBrpaZSe6ke"

print("=================================================")
print("TEXT ME BOT SETUP")
print("=================================================")
import requests

print("=================================================")
print("GETTING GROUP ID via Invitation Code")
print("=================================================")
print("1. Go to your WhatsApp Group Info -> Invite via Link.")
print("2. Copy the *last part* of the link (the random code).")
print("   Example: https://chat.whatsapp.com/LZ4KWNTLA8... -> LZ4KWNTLA8...")
print("\nUsing Invite Code: H8Z8SOf3YU6LlPE6WZYWfO")
invite_code = "H8Z8SOf3YU6LlPE6WZYWfO"

try:
    # Endpoint to get group info from invite code
    url = f"https://api.textmebot.com/send.php?apikey={API_KEY}&group_info={invite_code}"
    print(f"Querying: {url}")
    res = requests.get(url)
    print("\nResponse:")
    print(res.text)
    print("\nLook for 'Group ID' in the response (e.g. 188373...@g.us) and provide it to me.")
except Exception as e:
    print(f"Error fetching group ID: {e}")


