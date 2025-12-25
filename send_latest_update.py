from find_houses import HouseFinder
import json

def send_update():
    print("Loading existing listings to send update...")
    finder = HouseFinder()
    try:
        with open('listings.json', 'r') as f:
            finder.listings = json.load(f)
    except FileNotFoundError:
        print("No listings.json found.")
        return

    print(f"Loaded {len(finder.listings)} listings.")
    # finder.send_notifications() relies on internal config, let's peek at it if possible or just run it.
    # Since we can't easily peek without instantiating fully or parsing, we trust the file is updated.
    print("Initiating notification sequence...")
    finder.send_notifications()

if __name__ == "__main__":
    send_update()
