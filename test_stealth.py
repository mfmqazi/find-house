try:
    from playwright_stealth import stealth_sync
    print("Success: playwright_stealth imported")
except ImportError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Error: {e}")
