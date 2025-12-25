import json
import os

MASJIDS_FILE = 'masjids.json'
LISTINGS_FILE = 'listings.json'
OUTPUT_HTML = 'index.html'

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def generate_html():
    masjids = load_json(MASJIDS_FILE)
    listings = load_json(LISTINGS_FILE)
    
    # Organize listings by Masjid
    listings_by_masjid = {}
    for masjid in masjids:
        listings_by_masjid[masjid['name']] = []

    for listing in listings:
        # Check if nearby_masjids exists (it should)
        if 'nearby_masjids' in listing:
            for match in listing['nearby_masjids']:
                entry = listing.copy()
                entry['dist_to_this_masjid'] = match['distance']
                # Ensure the masjid name exists in our dict (handle potential mismatches/new masjids)
                if match['name'] not in listings_by_masjid:
                    listings_by_masjid[match['name']] = []
                listings_by_masjid[match['name']].append(entry)

    # Sort each group by distance
    for name in listings_by_masjid:
        listings_by_masjid[name].sort(key=lambda x: x.get('dist_to_this_masjid', 0))

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Phoenix House Finder (Live Update)</title>
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
        <div class="status-bar">Tracking {len(listings)} listings across {len(masjids)} Masjids</div>
    """
    
    count_display = 0
    for masjid_name, items in listings_by_masjid.items():
        if not items:
            continue
        count_display += 1
        html += f"""
        <div class="masjid-section">
            <div class="masjid-title">{masjid_name} · {len(items)} found</div>
            <div class="container">
        """
        for item in items:
            dist = item.get('dist_to_this_masjid', 0)
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
        
    if count_display == 0:
        html += '<div style="text-align:center; padding: 50px; color: #666;">No matching houses found in the current buffer. The script might still be running.</div>'

    html += """
    </body>
    </html>
    """
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_html()
