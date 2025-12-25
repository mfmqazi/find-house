import time
import os
from playwright.sync_api import sync_playwright

# Directory to store WhatsApp session data so you don't have to scan QR code every time
SESSION_DIR = os.path.join(os.getcwd(), "wa_session")

def send_whatsapp_message(group_name, message):
    """
    Sends a message to a specific WhatsApp group using Playwright.
    This method is robust and does not interfere with the user's mouse/keyboard
    because it interacts directly with the browser DOM.
    """
    with sync_playwright() as p:
        # Launch browser with persistent context to save login state
        # Added stealth arguments to avoid detection
        browser = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False, # Must be visible
            channel="chrome", 
            args=[
                "--start-maximized", 
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars"
            ],
            viewport=None # Use window size
        )
        
        page = browser.pages[0]
        
        try:
            print("Opening WhatsApp Web...")
            page.goto("https://web.whatsapp.com/", timeout=90000)
            print(f"Page Title: {page.title()}")
            
            # 1. Check for Login
            try:
                print("Waiting for WhatsApp to load... (Timeout: 600s / 10 mins)")
                
                # Loop to check status so we can print updates
                start_time = time.time()
                while time.time() - start_time < 600:
                    # Success Check: Search box OR Chat List
                    if (page.locator('div[contenteditable="true"][data-tab="3"]').is_visible() or 
                        page.locator('div[role="textbox"]').is_visible() or
                        page.locator('div[aria-label="Chat list"]').is_visible() or
                        page.locator('div[data-testid="chat-list"]').is_visible()):
                        print("✅ Logged in!")
                        break
                    
                    if page.locator('text=Loading your chats').is_visible():
                        print("⏳ Still loading chats... Please wait.")
                        time.sleep(2)
                        continue
                        
                    if page.locator('canvas[aria-label="Scan this QR code"]').is_visible():
                         print("👉 PLEASE SCAN THE QR CODE NOW!")
                         
                    time.sleep(1)
                else:
                    raise TimeoutError("Wait loop exceeded 600s")
                    
            except Exception as e:
                print(f"⚠️ Login/Load Error: {e}")
                print("Capturing screenshot for debug: login_debug.png")
                page.screenshot(path="login_debug.png")
                return

            # 2. Search for the Group
            print(f"Searching for group: '{group_name}'...")
            
            # Robust Search Box Location
            # We look for the search box in the left pane
            search_box = page.locator('div[contenteditable="true"][data-tab="3"]').first
            if not search_box.is_visible():
                # Fallback: look for any textbox in the side pane area (approximate)
                search_box = page.locator('div[role="textbox"]').first
            
            search_box.click()
            # Clear and type
            search_box.fill(group_name)
            time.sleep(1) # Wait for search results
            search_box.press("Enter")
            
            # 3. Verify we opened the chat
            time.sleep(1)
            
            # 4. Type the Message
            # Main chat input footer
            # Usually data-tab="10"
            message_box = page.locator('div[contenteditable="true"][data-tab="10"]')
            
            if not message_box.is_visible():
                 # Fallback
                 message_box = page.locator('footer div[contenteditable="true"]').first
            
            if not message_box.is_visible():
                print(f"❌ Could not find chat input for '{group_name}'.")
                return
            
            print("Typing message...")
            # We use fill or focus+type. 
            # Note: WhatsApp handles newlines with Shift+Enter. 
            # If we just fill, it might submit on Enter or might not handle newlines correctly if passed as one string.
            # Best practice: split by lines and shift+enter
            
            message_box.click()
            
            for line in message.split('\n'):
                message_box.type(line)
                message_box.press("Shift+Enter")
            
            # Remove the last Shift+Enter newline if needed, but usually fine.
            # Send
            message_box.press("Enter")
            print("✅ Message SENT.")
            
            # Wait a bit for send to register
            time.sleep(3)
            
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            # Save screenshot for debug
            page.screenshot(path="wa_error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    # Test
    # Replace with your EXACT Group Name
    TEST_GROUP_NAME = "My Test Group" 
    send_whatsapp_message(TEST_GROUP_NAME, "Hello from the new Bot!\nThis message is typed in the background.")
