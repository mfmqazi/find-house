from playwright.sync_api import sync_playwright

def debug_fsbo():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        url = "https://www.forsalebyowner.com/search/list/Phoenix-AZ/2-beds/2-baths/single-story"
        print(f"Going to {url}")
        
        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)
            
            # Save HTML
            content = page.content()
            with open("debug_fsbo.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("Saved debug_fsbo.html")
            
        except Exception as e:
            print(f"Error: {e}")
            
        browser.close()

if __name__ == "__main__":
    debug_fsbo()
