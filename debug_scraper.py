from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

def debug():
    ua = UserAgent()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=ua.random)
        page = context.new_page()
        
        # Try a simpler URL first or the target one
        url = "https://www.realtor.com/realestateandhomes-search/Phoenix_AZ/beds-3/baths-3/type-single-story-home"
        print(f"Going to {url}")
        
        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)
            
            content = page.content()
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("Saved debug_page.html")
            
            # Print page title
            print(f"Page Title: {page.title()}")
            
        except Exception as e:
            print(f"Error: {e}")
            
        browser.close()

if __name__ == "__main__":
    debug()
