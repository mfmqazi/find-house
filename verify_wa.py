from whatsapp_bot import send_whatsapp_message
import sys

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

GROUP_NAME = "Qazi Real Estate"

print("=================================================")
print("TESTING GROUP NOTIFICATION (ISOLATED BROWSER)")
print("=================================================")
print("Attempting to send to Group: 'Qazi Real Estate'")
print("This uses an ISOLATED browser window. It will NOT secure your mouse or type in other windows.")
print("Since you are logged in, this should be fast.")
print("=================================================")

try:
    send_whatsapp_message(GROUP_NAME, "✅ Final Test: Sending to Group via Independent Browser.\nIf you see this, the Group Integration is FIXED.")
    print("\nSUCCESS! Message sent to group.")
except Exception as e:
    print(f"\nFailed: {e}")
