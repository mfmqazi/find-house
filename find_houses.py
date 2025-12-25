import json
import time
import math
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

try:
    from playwright_stealth import stealth_sync
    HAS_STEALTH = True
except ImportError:
    HAS_STEALTH = False
    print("Notice: playwright-stealth not installed, using manual stealth method.")

# Configuration
MASJIDS_FILE = 'masjids.json'
LISTINGS_FILE = 'listings.json'
OUTPUT_HTML = 'index.html'
SEARCH_RADIUS_MILES = 5
# Cities to search
CITIES = ['Phoenix', 'Peoria', 'Glendale', 'Scottsdale', 'Chandler', 'Tempe']

class HouseFinder:
    def __init__(self):
        self.masjids = self.load_masjids()
        self.listings = []
        self.ua = UserAgent()

    def load_masjids(self):
        try:
            with open(MASJIDS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {MASJIDS_FILE} not found.")
            return []

    def get_coordinates(self, address):
        geolocator = Nominatim(user_agent="house_finder_bot_v2")
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                return location.latitude, location.longitude
        except Exception as e:
            print(f"Geocode error for {address}: {e}")
        return None, None

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 3958.8  # Earth radius in miles
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def get_nearby_masjids(self, lat, lon):
        nearby = []
        for masjid in self.masjids:
            if masjid.get('lat') and masjid.get('lon'):
                dist = self.haversine_distance(lat, lon, masjid['lat'], masjid['lon'])
                if dist <= SEARCH_RADIUS_MILES:
                    nearby.append({
                        'name': masjid['name'],
                        'distance': dist
                    })
        nearby.sort(key=lambda x: x['distance'])
        return nearby

    def scrape_realtor(self, page, city):
        print(f"--- Scraping Realtor.com for {city} ---")
        url = f"https://www.realtor.com/realestateandhomes-search/{city}_AZ/beds-2/baths-2/type-single-story-home"
        try:
            print(f"Navigating to {url}...")
            page.goto(url, timeout=90000)
            
            # Check for captcha or block
            if "unblockrequest" in page.content() or "captcha" in page.content().lower():
                print("⚠ DETECTED BLOCK/CAPTCHA on Realtor.com.")
                print("Please solve the CAPTCHA in the browser window if visible...")
                page.wait_for_timeout(15000) # Give user 15s to solve
            
            # Wait for content
            try:
                page.wait_for_selector('div[data-testid="property-card"]', timeout=10000)
            except:
                print("Timed out waiting for property-card. Content might be different or blocked.")

            cards = page.locator('div[data-testid="property-card"]').all()
            print(f"Found {len(cards)} cards on Realtor in {city}")
            
            for card in cards:
                try:
                    price = card.locator('[data-testid="card-price"]').inner_text(timeout=2000)
                    # Address is often split in spans
                    address_parts = card.locator('[data-testid="card-address"] [data-testid]').all_inner_texts()
                    if address_parts:
                        address = ", ".join(address_parts)
                    else:
                        address = card.locator('[data-testid="card-address"]').inner_text(timeout=2000).replace('\n', ', ')
                        
                    link_locator = card.locator('a[href^="/realestateandhomes-detail"]')
                    if link_locator.count() > 0:
                        link = "https://www.realtor.com" + link_locator.first.get_attribute('href')
                    else:
                        link = url
                    
                    img_locator = card.locator('img')
                    image = img_locator.first.get_attribute('src') if img_locator.count() > 0 else ""

                    self.process_listing(address, price, link, image, "Realtor.com", city)
                except Exception as e:
                    # print(f"Error parsing card: {e}")
                    continue
        except Exception as e:
            print(f"Realtor scrape error: {e}")

    def scrape_fsbo(self, page, city):
         print(f"--- Scraping ForSaleByOwner.com for {city} ---")
         # URL format: .../Phoenix-AZ/2-beds/2-baths/single-story
         url = f"https://www.forsalebyowner.com/search/list/{city}-AZ/2-beds/2-baths/single-story"
         try:
             page.goto(url, timeout=60000)
             # Wait for anything useful
             page.wait_for_timeout(3000)
             
             cards = page.locator('div[class*="card-"]').all()
             if not cards:
                 cards = page.locator('div.shadow.rounded-lg.relative.flex').all()

             print(f"Found {len(cards)} cards on FSBO in {city}")
             
             for card in cards:
                 try:
                     # New Robust Selectors
                     # Link is usually on the address <a>
                     link_el = card.locator('a[href^="/listing/"]').first
                     if not link_el.count():
                         continue

                     link = link_el.get_attribute('href')
                     
                     # Address is the text of that link, usually the first text node.
                     # The city/state is often in a child span. We must exclude it.
                     address = link_el.evaluate("el => el.childNodes[0].textContent").strip()

                     # Price is in a sibling/parent container but inside the card
                     # It has class "text-xl" and starts with $
                     price_el = card.locator('span.text-xl').filter(has_text="$").first
                     price = price_el.inner_text() if price_el.count() else "N/A"

                     # Image
                     img_el = card.locator('img').first
                     image = img_el.get_attribute('src') if img_el.count() else ""

                     if link and not link.startswith('http'):
                        link = "https://www.forsalebyowner.com" + link
                     
                     self.process_listing(address, price, link, image, "ForSaleByOwner", city)
                 except Exception as e:
                     print(f"FSBO card parse error: {e}")
                     continue
         except Exception as e:
             print(f"FSBO scrape error: {e}")

    def scrape_homes_com(self, page, city):
        print(f"--- Scraping Homes.com for {city} ---")
        # Homes.com URL: https://www.homes.com/phoenix-az/homes-for-sale/2-bedroom/?property_type=1&bathrooms=2g
        # property_type=1 is typically House/Single Family
        url = f"https://www.homes.com/{city.lower()}-az/homes-for-sale/2-bedroom/?property_type=1&bathrooms=2g"
        
        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(3000)
            
            # Homes.com selectors
            cards = page.locator('article[data-testid="listing-card"]').all()
            if not cards:
                cards = page.locator('.placards-list ul li article').all()
            
            print(f"Found {len(cards)} cards on Homes.com in {city}")
            
            for card in cards:
                try:
                    price = card.locator('.price-container').first.inner_text()
                    address = card.locator('.property-name').first.inner_text()
                    link_el = card.locator('a').first
                    link = "https://www.homes.com" + link_el.get_attribute('href')
                    
                    # Image
                    img_el = card.locator('img').first
                    image = img_el.get_attribute('src')

                    self.process_listing(address, price, link, image, "Homes.com", city)
                except:
                    continue
        except Exception as e:
            print(f"Homes.com scrape error: {e}")

    def process_listing(self, address, price, link, image, source, city):
        if any(l['link'] == link for l in self.listings):
            return

        # basic cleaning
        address = address.strip()

        # print(f"Processing: {address}...") # Debug
        lat, lon = self.get_coordinates(address)
        if not lat:
            # Try appending city/state
            if city.lower() not in address.lower():
                addr_full = f"{address}, {city}, AZ"
                # print(f"  Geocode retry with: {addr_full}")
                lat, lon = self.get_coordinates(addr_full)
        
        if lat and lon:
            nearby_list = self.get_nearby_masjids(lat, lon)
            if nearby_list:
                print(f"✅ MATCH: {address} is near {nearby_list[0]['name']}")
                self.listings.append({
                    'address': address,
                    'price': price,
                    'link': link,
                    'image': image,
                    'source': source,
                    'nearby_masjids': nearby_list,
                    'city': city
                })
            else:
                # Debug: why not?
                # Calculate distance to nearest just for info
                nearest_dist = 999
                for m in self.masjids:
                    if m.get('lat'):
                        d = self.haversine_distance(lat, lon, m['lat'], m['lon'])
                        if d < nearest_dist: nearest_dist = d
                print(f"  Skipped {address}: Nearest Masjid is {nearest_dist:.2f} mi away (> {SEARCH_RADIUS_MILES})")
        else:
            print(f"  ❌ Geocode failed for {address}")
            
        time.sleep(0.5) # Slight delay to be nice to Nominatim 

    def save_listings(self):
        with open(LISTINGS_FILE, 'w') as f:
            json.dump(self.listings, f, indent=4)
        print(f"Saved {len(self.listings)} listings to {LISTINGS_FILE}")

    def run(self):
        # HEADLESS=False is crucial for Realtor.com
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500) 
            # Fixed modern User Agent
            fixed_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
            context = browser.new_context(
                user_agent=fixed_ua,
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/Phoenix'
            )
            
            # Enable stealth manually
            page = context.new_page()
            
            if HAS_STEALTH:
                stealth_sync(page)
            
            # Manual Stealth: Overwrite webdriver property
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            for city in CITIES:
                # self.scrape_realtor(page, city)
                # self.save_listings()
                self.scrape_fsbo(page, city)
                self.save_listings()
                self.scrape_homes_com(page, city)
                self.save_listings()
            
            browser.close()

        self.generate_html()
        self.send_notifications()

    def generate_html(self):
        listings_by_masjid = {}
        for masjid in self.masjids:
            listings_by_masjid[masjid['name']] = []

        for listing in self.listings:
            for match in listing['nearby_masjids']:
                entry = listing.copy()
                entry['dist_to_this_masjid'] = match['distance']
                listings_by_masjid[match['name']].append(entry)

        for name in listings_by_masjid:
            listings_by_masjid[name].sort(key=lambda x: x['dist_to_this_masjid'])

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Phoenix House Finder</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background-color: #f3f4f6; color: #1f2937; margin: 0; padding: 20px; }}
                h1 {{ text-align: center; color: #db2777; margin-bottom: 20px; }}
                .status-bar {{ text-align: center; color: #6b7280; margin-bottom: 40px; font-size: 0.9em; }}
                .masjid-section {{ margin: 40px auto; max-width: 1200px; }}
                .masjid-title {{ font-size: 1.5em; color: #4b5563; border-left: 5px solid #db2777; padding-left: 15px; margin-bottom: 20px; font-weight: bold; background: white; padding: 10px 15px; border-radius: 0 8px 8px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
                .container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 25px; }}
                .card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; display: flex; flex-direction: column; }}
                .card:hover {{ transform: translateY(-4px); box-shadow: 0 10px 15px rgba(0,0,0,0.1); }}
                .card img {{ width: 100%; height: 200px; object-fit: cover; }}
                .card-content {{ padding: 20px; flex-grow: 1; display: flex; flex-direction: column; }}
                .source-badge {{ font-size: 0.75em; text-transform: uppercase; font-weight: bold; color: #9ca3af; margin-bottom: 5px; }}
                .price {{ font-size: 1.5em; color: #be185d; font-weight: 800; margin-bottom: 5px; }}
                .address {{ color: #4b5563; font-size: 1.1em; line-height: 1.4; margin-bottom: 15px; }}
                .dist-badge {{ align_self: flex-start; background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 20px; font-size: 0.85em; font-weight: 600; margin-bottom: 15px; }}
                .actions {{ margin-top: auto; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
                .btn {{ padding: 10px; text-align: center; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 0.9em; transition: background 0.2s; }}
                .btn-view {{ background: #f3f4f6; color: #374151; }}
                .btn-view:hover {{ background: #e5e7eb; }}
                .btn-wa {{ background: #22c55e; color: white; }}
                .btn-wa:hover {{ background: #16a34a; }}
            </style>
        </head>
        <body>
            <h1>Compatible Homes Near Masjids</h1>
            <div class="status-bar">Tracking {len(self.listings)} listings across {len(self.masjids)} Masjids</div>
        """
        
        has_listings = False
        for masjid_name, items in listings_by_masjid.items():
            if not items:
                continue
            has_listings = True
            html += f"""
            <div class="masjid-section">
                <div class="masjid-title">{masjid_name} · {len(items)} found</div>
                <div class="container">
            """
            for item in items:
                dist = item['dist_to_this_masjid']
                wa_text = f"Check this house near {masjid_name} ({dist:.2f} mi): {item['address']} - {item['price']} - {item['link']}"
                wa_link = f"https://wa.me/?text={wa_text}"
                image_url = item.get('image', '')
                if not image_url or "http" not in image_url:
                    image_url = "https://via.placeholder.com/300x200?text=No+Image"

                html += f"""
                <div class="card">
                    <img src="{image_url}" alt="Home">
                    <div class="card-content">
                        <div class="source-badge">{item['source']}</div>
                        <div class="price">{item['price']}</div>
                        <div class="address">{item['address']}</div>
                        <div class="dist-badge">📍 {dist:.2f} miles away</div>
                        <div class="actions">
                            <a href="{item['link']}" target="_blank" class="btn btn-view">View details</a>
                            <a href="{wa_link}" target="_blank" class="btn btn-wa">WhatsApp</a>
                        </div>
                    </div>
                </div>
                """
            html += "</div></div>"
            
        if not has_listings:
            html += '<div style="text-align:center; padding: 50px; color: #666;">No matching houses found in this run. Please try running the script again or check the browser for captchas.</div>'

        html += """
        </body>
        </html>
        """
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Generated {OUTPUT_HTML} Grouped by Masjid.")

    def send_notifications(self):
        if not self.listings:
            return

        print(f"--- Sending Notifications for {len(self.listings)} listings ---")
        
        # WhatsApp Automation via TextMeBot API
        try:
            from textmebot_interface import send_textmebot_message
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            
            # --- CONFIGURATION FROM ENV ---
            TEXTMEBOT_APIKEY = os.getenv("TEXTMEBOT_APIKEY")
            TARGET_PHONE = os.getenv("TEXTMEBOT_TARGET")
            
            if not TEXTMEBOT_APIKEY:
                print("⚠️ Error: TEXTMEBOT_APIKEY not found in .env file.")
                return

            # Group listings by Masjid
            by_masjid = {}
            for item in self.listings:
                # nearby_masjids is a list of {'name':..., 'distance':...}
                for masjid in item.get('nearby_masjids', []):
                    m_name = masjid['name']
                    if m_name not in by_masjid:
                        by_masjid[m_name] = []
                    
                    # Store listing with specific distance for this masjid
                    entry = item.copy()
                    entry['sort_dist'] = masjid['distance']
                    by_masjid[m_name].append(entry)
            
            # Sort Masjids alphabetically
            sorted_masjids = sorted(by_masjid.keys())
            
            full_msg = f"🏠 Found {len(self.listings)} homes!\n"
            
            for m_name in sorted_masjids:
                entries = by_masjid[m_name]
                # Sort by distance
                entries.sort(key=lambda x: x['sort_dist'])
                
                full_msg += f"\n🕋 *{m_name}* ({len(entries)})\n"
                for entry in entries:
                    dist = entry['sort_dist']
                    price = entry['price']
                    # Truncate address if too long
                    addr = entry['address'][:30] + "..." if len(entry['address']) > 30 else entry['address']
                    link = entry['link']
                    full_msg += f"📍 {dist:.2f}mi | {price}\n{link}\n"
            
            full_msg += f"\nOpen http://localhost:8080 for full details."
            full_msg += "\nSent automatically by Musaddique's Bot"

            print(f"Sending via TextMeBot to Group ({TARGET_PHONE})...")
            send_textmebot_message(TEXTMEBOT_APIKEY, TARGET_PHONE, full_msg)
            
        except ImportError:
            print("Could not import textmebot_interface.")
        except Exception as e:
            print(f"WhatsApp send failed: {e}")

if __name__ == "__main__":
    import sys
    # Force UTF-8 encoding for stdout/stderr to avoid charmap errors on Windows
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

    finder = HouseFinder()
    finder.run()
