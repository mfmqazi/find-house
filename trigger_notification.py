from textmebot_interface import send_textmebot_message
import json
import sys
import os
from dotenv import load_dotenv

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()

LISTINGS_FILE = 'listings.json'
TEXTMEBOT_APIKEY = os.getenv("TEXTMEBOT_APIKEY")
TARGET_PHONE = os.getenv("TEXTMEBOT_TARGET")

def load_listings():
    try:
        with open(LISTINGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def send_notification():
    listings = load_listings()
    if not listings:
        print("No listings to send.")
        return

    print(f"Loaded {len(listings)} listings from {LISTINGS_FILE}")
    
    # Group listings by Masjid
    by_masjid = {}
    for item in listings:
        for masjid in item.get('nearby_masjids', []):
            m_name = masjid['name']
            if m_name not in by_masjid:
                by_masjid[m_name] = []
            
            entry = item.copy()
            entry['sort_dist'] = masjid['distance']
            by_masjid[m_name].append(entry)
    
    sorted_masjids = sorted(by_masjid.keys())
    
    full_msg = f"🏠 Found {len(listings)} homes!\n"
    
    for m_name in sorted_masjids:
        entries = by_masjid[m_name]
        entries.sort(key=lambda x: x['sort_dist'])
        
        full_msg += f"\n🕋 *{m_name}* ({len(entries)})\n"
        for entry in entries:
            dist = entry['sort_dist']
            price = entry['price']
            addr = entry['address'][:30] + "..." if len(entry['address']) > 30 else entry['address']
            link = entry['link']
            full_msg += f"📍 {dist:.2f}mi | {price}\n{link}\n"
    
    full_msg += f"\nOpen http://localhost:8080 for details."
    full_msg += "\nSent automatically by Musaddique's Bot"

    print(f"Sending via TextMeBot to {TARGET_PHONE}...")
    
    try:
        send_textmebot_message(TEXTMEBOT_APIKEY, TARGET_PHONE, full_msg)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_notification()
