import json
import pywhatkit
import time

LISTINGS_FILE = 'listings.json'
# WA_TARGET = "H8Z8SOf3YU6LlPE6WZYWfO" # Group ID
WA_TARGET = "H8Z8SOf3YU6LlPE6WZYWfO" 

def load_listings():
    try:
        with open(LISTINGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def send_test_notification():
    listings = load_listings()
    
    if not listings:
        print("No listings found in file, using dummy data for test.")
        listings = [{
            'price': '$TEST_PRICE',
            'address': '123 Test Lane',
            'link': 'http://test.link'
        }]

    print(f"Found {len(listings)} listings. Sending test message...")

    msg = f"🔔 TEST NOTIFICATION: Checking WhatsApp integration.\n"
    msg += f"Found {len(listings)} homes in the latest scan (cached).\n"
    
    # Just show first one as example
    if listings:
        item = listings[0]
        msg += f"Example: {item['price']} - {item['address']}\n{item['link']}\n"
    
    msg += "\nSent automatically by a program written by Musaddique Qazi"

    try:
        # Using sendwhatmsg_to_group_instantly for group
        # Note: This opens a browser tab.
        print(f"Sending to Group ID: {WA_TARGET}")
        print("Please ensure you are logged into WhatsApp Web in your default browser.")
        print("Do not touch the mouse/keyboard while the script runs.")
        
        pywhatkit.sendwhatmsg_to_group_instantly(WA_TARGET, msg, wait_time=40, tab_close=False)
        print("Message request sent to browser.")
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    send_test_notification()
