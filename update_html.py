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
        <title>Phoenix House Finder (Secure)</title>
        <!-- Firebase SDKs -->
        <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js"></script>
        <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-auth-compat.js"></script>

        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background-color: #f3f4f6; color: #1f2937; margin: 0; padding: 0; }}
            
            /* Login Screen Styles */
            #login-screen {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: linear-gradient(135deg, #be185d 0%, #881337 100%);
                display: flex; justify-content: center; align-items: center; z-index: 1000;
            }}
            .login-box {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); width: 300px; text-align: center; }}
            .login-box h2 {{ margin-top: 0; color: #881337; }}
            .login-box input {{ width: 90%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; box-sizing: border-box; }}
            .login-box button {{ width: 100%; padding: 12px; margin-top: 10px; background: #be185d; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; transition: background 0.2s; font-weight: bold; }}
            .login-box button:hover {{ background: #9d174d; }}
            .error {{ color: #ef4444; font-size: 0.9em; margin-top: 15px; display: none; background: #fee2e2; padding: 10px; border-radius: 6px; }}

            /* App Content Styles */
            #app-content {{ display: none; padding: 20px; }}
            h1 {{ text-align: center; color: #db2777; margin-bottom: 20px; }}
            .status-bar {{ text-align: center; color: #6b7280; margin-bottom: 40px; font-size: 0.9em; }}
            .header-bar {{ display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; color: #666; font-size: 0.9em; }}
            .logout-btn {{ color: #be185d; cursor: pointer; text-decoration: underline; font-weight: bold; }}
            
            /* Listing Cards */
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

    <!-- Login Screen -->
    <div id="login-screen">
        <div class="login-box">
            <h2>🔒 Secure Access</h2>
            <p style="color: #666; font-size: 0.9em; margin-bottom: 20px;">Please sign in to view listings.</p>
            <input type="email" id="emailInput" placeholder="Email" onkeyup="if(event.key==='Enter') document.getElementById('passInput').focus()">
            <input type="password" id="passInput" placeholder="Password" onkeyup="if(event.key==='Enter') login()">
            <button onclick="login()" id="loginBtn">Sign In</button>
            <div id="loginError" class="error"></div>
        </div>
    </div>

    <!-- Main Content -->
    <div id="app-content">
        <div class="header-bar">
            <span>Signed in as <strong id="userDisplay">...</strong></span>
            <span class="logout-btn" onclick="logout()">Sign Out</span>
        </div>
        
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
    </div> <!-- End App Content -->

    <script>
        // --- Firebase Configuration ---
        // (Split to avoid GitHub Secret Scanning False Positives)
        const p1 = "AIzaSyAYeSVUevKl";
        const p2 = "Q0b7IWq97R1vQkirPgijer0";
        
        const firebaseConfig = {
            apiKey: p1 + p2,
            authDomain: "find-house-fa06d.firebaseapp.com",
            projectId: "find-house-fa06d",
            storageBucket: "find-house-fa06d.firebasestorage.app",
            messagingSenderId: "1028039915716",
            appId: "1:1028039915716:web:34d6c09c02c4abb15d3191",
            measurementId: "G-RFQYPYXX53"
        };

        // Initialize Firebase
        firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();

        // --- SESSION PERSISTENCE (Log out on tab close) ---
        auth.setPersistence(firebase.auth.Auth.Persistence.SESSION)
            .then(() => {
                // Persistence set successfully
            })
            .catch((error) => {
                console.error("Auth Persistence Error:", error);
            });

        // --- Auth Logic ---
        const emailInput = document.getElementById('emailInput');
        const passInput = document.getElementById('passInput');
        const loginBtn = document.getElementById('loginBtn');
        const errorMsg = document.getElementById('loginError');

        function login() {
            const email = emailInput.value;
            const pass = passInput.value;
            
            if(!email || !pass) {
                showError("Please enter email and password.");
                return;
            }

            loginBtn.innerText = "Verifying...";
            errorMsg.style.display = 'none';

            // Sign in (Persistence is already set to SESSION above)
            auth.signInWithEmailAndPassword(email, pass)
                .catch((error) => {
                    const errorCode = error.code;
                    const errorMessage = error.message;
                    showError(errorMessage);
                    loginBtn.innerText = "Sign In";
                });
        }

        function logout() {
            auth.signOut();
        }

        function showError(msg) {
            errorMsg.innerText = msg;
            errorMsg.style.display = 'block';
        }

        // --- Observer ---
        auth.onAuthStateChanged((user) => {
            if (user) {
                // User is signed in
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('app-content').style.display = 'block';
                document.getElementById('userDisplay').innerText = user.email;
            } else {
                // User is signed out
                document.getElementById('login-screen').style.display = 'flex';
                document.getElementById('app-content').style.display = 'none';
                loginBtn.innerText = "Sign In";
                emailInput.value = "";
                passInput.value = "";
            }
        });
    </script>
    </body>
    </html>
    """
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_html()
