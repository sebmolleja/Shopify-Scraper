import requests, time, re, datetime
from dotenv import load_dotenv
import os

load_dotenv()

URL = os.getenv("URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SLEEP = 20 # change time as needed
seen = set()

def fetch_ids():
    html = requests.get(URL).text
    product_urls = set(re.findall(r'"url":"(\/products\/.*?)"', html))
    return product_urls

def parse_product_name(url):
    name = url.split("/")[-1].replace("-", " ").title()
    return name

def notify_discord(new_items):
    if not new_items:
        return
    
    messages = []
    for item in new_items:
        full_url = f"https://unico13.com{item}"
        product_name = parse_product_name(item)
        
        msg =   f"🆕 **New Product Available!**\n" \
                f"⌚️**{product_name}**\n" \
                f"🔗 {full_url}\n" \
                f"--------------------------"
        messages.append(msg)

    content = "\n\n".join(messages) + "\n\n*Stay tuned for more drops! 🚀*"

    response = requests.post(WEBHOOK_URL, json={"content": content})
    if response.status_code != 204:
        print("Failed to send Discord notification:", response.text)

def monitor():
    global seen
    seen = fetch_ids()
    log_message("Initial product list fetched. Monitoring for new products...")

    while True:
        time.sleep(SLEEP)
        current = fetch_ids()

        # simulate a new product drop for testing
        # fake_product = "/products/fake-test-product-123"
        # current.add(fake_product)  # Inject fake product here!

        log_message(f"Fetched product list. Total products found: {len(current)}")
        
        new_items = current - seen
        if new_items:
            log_message(f"New products found! {new_items}")
            notify_discord(new_items)
            seen.update(new_items)


def log_message(message):
    timestamp = datetime.datetime.now()
    log_entry = f"[{timestamp}] {message}"
    
    print(log_entry)
    
    with open("log.txt", "a") as log_file:
        log_file.write(log_entry + "\n")


def test_notify():
    test_product = "/products/nike-triax-speed-50-regular-watch-blue"
    notify_discord([test_product])

if __name__ == "__main__":
    print("🔍 Monitoring started...")
    monitor()

    # print("🔧 Running manual Discord notification test...")
    # test_notify()
