import time
import csv
import random
import re
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

def configure_chrome_options() -> uc.ChromeOptions:
    """
    Configures advanced stealth settings for undetected_chromedriver.
    """
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return options

def sanitize_numeric_string(text: str) -> str:
    """
    Strips non-numeric characters from a string to isolate clean numbers (e.g., '1 250 000 zł' -> '1250000').
    """
    if not text or text == 'N/A':
        return 'N/A'
    cleaned = re.sub(r'[^\d]', '', text)
    return cleaned if cleaned else 'N/A'

def fetch_listings_from_page(driver: uc.Chrome, page_url: str) -> list:
    """
    Extracts raw property metrics using flexible HTML structures to prevent layout shift breaks.
    """
    print(f"[PAGE EXPLORER] Navigating to: {page_url}")
    driver.get(page_url)
    
    # Human-like random scrolling sequence
    time.sleep(random.uniform(5.0, 7.0))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
    time.sleep(random.uniform(1.0, 2.0))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 1.5);")
    time.sleep(random.uniform(1.0, 2.0))
    
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    
    # Find all links pointing directly to single offer pages
    all_links = soup.find_all('a', href=re.compile(r'/pl/oferta/'))
    
    if not all_links:
        print("[WARNING] No listing links found using broad pattern matching selectors.")
        return []

    extracted_properties = []
    processed_urls = set() # Prevent capturing duplicates from the same page card
    
    for link_node in all_links:
        try:
            url_path = link_node['href']
            if not url_path.startswith('http'):
                url = "https://www.otodom.pl" + url_path
            else:
                url = url_path
                
            if url in processed_urls:
                continue
                
            # Attempt to find parent container card holding this specific link
            card = link_node.find_parent(['article', 'div', 'li'], class_=lambda c: c and ('listing' in c.lower() or 'item' in c.lower() or 'card' in c.lower()))
            if not card:
                card = link_node.find_parent() # Fallback to immediate parent node

            # 1. Title Extraction
            title = 'N/A'
            title_node = card.find(['h3', 'p', 'span'], class_=lambda c: c and ('title' in c.lower() or 'heading' in c.lower()))
            if title_node:
                title = title_node.text.strip()
            else:
                # Fallback to the link text or any text inside the card structure
                title = link_node.text.strip()
                if len(title) < 10: # If text is too short, look for text inside headers
                    h_tag = card.find(['h3', 'h2'])
                    if h_tag: title = h_tag.text.strip()

            if title == 'N/A' or len(title) < 5:
                continue

            # 2. Valuation Data Extraction
            total_price = 'N/A'
            price_per_sqm = 'N/A'
            
            # Look for price tokens inside text
            card_text = card.text
            price_matches = re.findall(r'([\d\s ]+)\s*zł', card_text)
            
            if price_matches:
                # Usually the largest number or the first one is the total price
                clean_prices = [sanitize_numeric_string(p) for p in price_matches if len(sanitize_numeric_string(p)) > 2]
                if clean_prices:
                    total_price = clean_prices[0]
                    if len(clean_prices) > 1:
                        price_per_sqm = clean_prices[1]

            # 3. Technical Specs (Rooms & Area)
            rooms = 'N/A'
            area = 'N/A'
            
            rooms_match = re.search(r'(\d+)\s*(?:pokój|pokoje|pokoi|pok\.)', card_text.lower())
            if rooms_match:
                rooms = rooms_match.group(1)
            elif 'kawalerka' in title.lower() or 'kawalerka' in card_text.lower():
                rooms = '1'

            area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*m²', card_text.lower())
            if area_match:
                area = area_match.group(1).replace(',', '.')

            processed_urls.add(url)
            extracted_properties.append({
                'Title': title[:120],
                'Total Price (PLN)': total_price,
                'Price per SQM (PLN)': price_per_sqm,
                'Rooms': rooms,
                'Area (SQM)': area,
                'URL': url
            })
            
        except Exception as item_error:
            continue
            
    return extracted_properties

def save_dataset_to_csv(dataset: list, filename: str):
    """
    Commits compiled application database lists straight into local flat CSV files.
    """
    if not dataset:
        print("[WARNING] Compiled stream is empty. Aborting save sequence.")
        return
        
    fields = ['Title', 'Total Price (PLN)', 'Price per SQM (PLN)', 'Rooms', 'Area (SQM)', 'URL']
    
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(dataset)
        print(f"\n[SUCCESS] Extracted database stream verified at file: ./{filename}")
    except IOError as io_error:
        print(f"[CRITICAL ERROR] Master file IO driver failure: {io_error}")

if __name__ == "__main__":
    # --- CONFIGURATION HYPERPARAMETERS ---
    MAX_PAGES_TO_SCRAPE = 15  
    OUTPUT_FILE_PATH = "warsaw_detailed_properties.csv"
    # -------------------------------------
    
    base_endpoint = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa/warszawa/warszawa"
    chrome_options = configure_chrome_options()
    
    compiled_dataset = []
    
    try:
        driver = uc.Chrome(options=chrome_options, headless=False)
        print(f"--- STARTING ROBUST FAST SCRAPER: Indexing {MAX_PAGES_TO_SCRAPE} pages ---")
        
        for page_number in range(1, MAX_PAGES_TO_SCRAPE + 1):
            page_url = f"{base_endpoint}?page={page_number}" if page_number > 1 else base_endpoint
            page_offers = fetch_listings_from_page(driver, page_url)
            
            if not page_offers:
                print(f"[WARNING] Pagination pipeline terminated at index link {page_number}.")
                break
                
            compiled_dataset.extend(page_offers)
            print(f"[PROGRESS] Page index {page_number} fully integrated. Active stream size: {len(compiled_dataset)}")
            
        save_dataset_to_csv(compiled_dataset, OUTPUT_FILE_PATH)
        
    except Exception as master_error:
        print(f"[GLOBAL EXCEPTION] Pipeline cluster crashed: {master_error}")
    finally:
        if 'driver' in locals():
            driver.quit()