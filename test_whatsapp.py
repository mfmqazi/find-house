import time

def test_whatsapp():
    print("--- WhatsApp Notification Test ---")
    try:
        import pywhatkit
        print("✅ pywhatkit is installed.")
    except ImportError:
        print("❌ pywhatkit is NOT installed. Please run: pip install pywhatkit")
        return

    print("\nTo send a message, we need a Target.")
    print("1. Phone Number (e.g. +14805551234)")
    print("2. Group Invite ID (from the invite link, e.g. 'LZ4...')\n")
    
    choice = input("Enter 1 for Phone, 2 for Group: ").strip()
    target = input("Enter the Number or Group ID: ").strip()
    
    msg = "This is a test message from find_houses.py automated system."
    
    print(f"\nAttempting to send to {target} in 20 seconds...")
    print("PLEASE ENSURE:")
    print("1. You are logged into WhatsApp Web in your DEFAULT browser.")
    print("2. You do not touch the mouse/keyboard once the browser opens.")
    
    try:
        if choice == '2':
            pywhatkit.sendwhatmsg_to_group_instantly(target, msg, wait_time=20, tab_close=True)
        else:
            pywhatkit.sendwhatmsg_instantly(target, msg, wait_time=20, tab_close=True)
        print("\n✅ Message sent command issued.")
    except Exception as e:
        print(f"\n❌ Failed: {e}")

if __name__ == "__main__":
    test_whatsapp()
