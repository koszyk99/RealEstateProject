import time
import json
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

# Target URL
url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa/warszawa/warszawa"

print("Launching Undetected Chrome via Selenium...")

# Configure undetected chrome options
options = uc.ChromeOptions()
options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

try:
    # Launch browser in visible mode
    driver = uc.Chrome(options=options, headless=False)

    print(f"Entering the site: {url}")
    driver.get(url)

    # Wait for the initial page structure to load
    print("Waiting for page source...")
    time.sleep(7)

    # Extract HTML source
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')

    # Find the hidden JSON-LD script containing all listings data
    json_script = soup.find('script', type='application/ld+json')

    if json_script:
        # Parse the raw text into a Python dictionary
        data = json.loads(json_script.string)
        
        # Navigate through the schema graph to find the Product info
        graph = data.get('@graph', [])
        product_data = next((item for item in graph if item.get('@type') == 'Product'), None)
        
        if product_data and 'offers' in product_data:
            offers_list = product_data['offers'].get('offers', [])
            
            print("-" * 50)
            print(f"Success! Extracted {len(offers_list)} listings from structural JSON data.")
            print("-" * 50)
            
            # Loop through each offer inside the JSON data
            for offer in offers_list:
                title = offer.get('name', 'No title found.')
                price = offer.get('price', 'No price found.')
                link = offer.get('url', 'No link found.')
                
                # Extract price per square meter if available
                price_spec = offer.get('priceSpecification', {})
                price_per_m = price_spec.get('price', 'No info')
                
                # Format price fields nicely
                formatted_price = f"{price} PLN" if isinstance(price, (int, float)) else price
                formatted_price_per_m = f"{price_per_m} zł/m²" if isinstance(price_per_m, (int, float)) else price_per_m
                
                # Print result set to console
                print(f"🏠 TITLE: {title}")
                print(f"💰 PRICE: {formatted_price} ({formatted_price_per_m})")
                print(f"🔗 LINK:  {link}")
                print("-" * 50)
        else:
            print("Error: Could not find the 'Product' section inside the JSON object.")
    else:
        print("Error: Could not find <script type='application/ld+json'> in the page source.")

except Exception as e:
    print(f"An error occurred during execution: {e}")

finally:
    if 'driver' in locals():
        print("Closing the browser...")
        driver.quit()