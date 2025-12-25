# House Finder for Masjids

This tool scans for single-story, 2+ Bedroom, 2+ Bath homes within 5 miles of selected Masjids in the Phoenix Valley.

## Sources
- **Realtor.com**: (Often requires Captcha solving)
- **ForSaleByOwner.com**: (Works well)
- **Homes.com**: (Works well)

## How to Run
1. Open a terminal in this folder.
2. Run:
   ```powershell
   python find_houses.py
   ```
3. A browser window will open. **Do NOT close it.**
   - If Realtor.com asks for a Captcha, click "I am human".
   - The script will automatically browse through cities.
4. When finished, it generates `index.html`.
5. Open the results:
   ```powershell
   start index.html
   ```

## Configuration
- **Masjids**: Edit `masjids.json` to add/remove Masjids.
- **Email**: Set `EMAIL_USER` and `EMAIL_PASS` environment variables to receive email alerts.

## Note on Zillow/Redfin
Refrain from using personal credentials for scraping as it carries a high risk of account bans. This script uses public search pages and "stealth" browsing to access data safely.
