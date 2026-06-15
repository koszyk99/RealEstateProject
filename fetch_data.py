import time
import json
import csv
import random
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


def fetch_listings_from_page(driver: uc.Chrome, page_url: str) -> list:
    """
    Extracts basic listing offers from a single search result page using JSON-LD metadata.
    """
    print(f"[PAGE EXPLORER] Navigating to: {page_url}")
    driver.get(page_url)
    
    # Natural human delays and behavior emulation
    time.sleep(random.uniform(4.5, 6.5))
    driver.execute_script("window.scrollTo(0, 350);")
    time.sleep(random.uniform(1.0, 2.0))
    
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    
    json_script = soup.find('script', type='application/ld+json')
    if not json_script:
        print("[WARNING] Could not find application/ld+json block on this page.")
        return []

    try:
        data = json.loads(json_script.string)
        graph = data.get('@graph', [])
        product_data = next((item for item in graph if item.get('@type') == 'Product'), None)
        
        if product_data and 'offers' in product_data:
            return product_data['offers'].get('offers', [])
    except Exception as error:
        print(f"[ERROR] Failed to parse JSON-LD structural data: {error}")
        
    return []


def fetch_detailed_property_data(driver: uc.Chrome, property_url: str) -> dict:
    """
    Navigates directly into a single property listing URL and extracts deep details from __NEXT_DATA__.
    """
    print(f"[DETAILED SCRAPER] Fetching individual item: {property_url}")
    
    # Anti-ban sleep offset to prevent Cloudflare rate-limiting
    time.sleep(random.uniform(3.5, 5.5))
    
    detailed_info = {
        'Rooms': 'N/A',
        'Floor': 'N/A',
        'Build Year': 'N/A',
        'Ownership': 'N/A',
        'Description': 'N/A'
    }
    
    try:
        driver.get(property_url)
        time.sleep(random.uniform(2.5, 4.0))
        
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        
        # Extract backend state payload from Next.js hydration script tag
        next_data_script = soup.find('script', id='__NEXT_DATA__')
        
        if next_data_script:
            page_json = json.loads(next_data_script.string)
            
            # Traversal inside NextJS state tree for listing features dictionary
            ad_context = page_json.get('props', {}).get('pageProps', {}).get('ad', {})
            if not ad_context:
                # Fallback path if the application tree structure varies
                ad_context = page_json.get('props', {}).get('pageProps', {}).get('fallback', {}).get('ad', {})
            
            if ad_context:
                # 1. Clean HTML markup formatting elements out of description text
                raw_description = ad_context.get('description', 'N/A')
                if raw_description and raw_description != 'N/A':
                    clean_desc = BeautifulSoup(raw_description, "html.parser").text
                    detailed_info['Description'] = clean_desc.strip().replace('\n', ' ')[:500] + "..."
                
                # 2. Extract specific housing parameters array items
                characteristics = ad_context.get('characteristics', [])
                for item in characteristics:
                    label = item.get('label', '').lower()
                    value = item.get('value', 'N/A')
                    
                    if 'liczba pokoi' in label or 'rooms' in label:
                        detailed_info['Rooms'] = value
                    elif 'piętro' in label or 'floor' in label:
                        detailed_info['Floor'] = value
                    elif 'rok budowy' in label or 'build' in label:
                        detailed_info['Build Year'] = value
                    elif 'forma własności' in label or 'ownership' in label:
                        detailed_info['Ownership'] = value
                        
        # Secondary fallback layer if target state node is empty
        if detailed_info['Rooms'] == 'N/A' and detailed_info['Description'] == 'N/A':
            desc_element = soup.find('div', attrs={"data-cy": "adPageAdDescriptionDataForm"})
            if desc_element:
                detailed_info['Description'] = desc_element.text.strip().replace('\n', ' ')[:500] + "..."
                
    except Exception as error:
        print(f"[ERROR] Failed to extract subpage detailed content: {error}")
        
    return detailed_info


def save_dataset_to_csv(dataset: list, filename: str):
    """
    Saves the final fully compiled dataset block directly to a local CSV spreadsheet file.
    """
    if not dataset:
        print("[WARNING] Combined database stream empty. Skipping save sequence.")
        return
        
    fields = ['Title', 'Total Price (PLN)', 'Price per SQM (PLN)', 'Rooms', 'Floor', 'Build Year', 'Ownership', 'URL', 'Description']
    
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(dataset)
        print(f"\n[PIPELINE SUCCESS] Complete storage dump verified at path: ./{filename}")
    except IOError as io_error:
        print(f"[CRITICAL ERROR] File writer system permissions block: {io_error}")


if __name__ == "__main__":
    # --- CONFIGURATION HYPERPARAMETERS ---
    MAX_PAGES_TO_SCRAPE = 2  # Set how many catalog page loops you want to traverse
    OUTPUT_FILE_PATH = "warsaw_detailed_properties.csv"
    # -------------------------------------
    
    base_endpoint = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa/warszawa/warszawa"
    chrome_options = configure_chrome_options()
    
    compiled_dataset = []
    collected_offers_metadata = []
    
    try:
        driver = uc.Chrome(options=chrome_options, headless=False)
        
        # PHASE 1: COLLECT TARGET METADATA LINK STREAMS ACROSS PACINATION INDEX
        print(f"--- PHASE 1: Crawling total index pages limit: {MAX_PAGES_TO_SCRAPE} ---")
        for page_number in range(1, MAX_PAGES_TO_SCRAPE + 1):
            page_url = f"{base_endpoint}?page={page_number}" if page_number > 1 else base_endpoint
            
            raw_offers = fetch_listings_from_page(driver, page_url)
            if not raw_offers:
                print(f"[WARNING] Pagination block break encountered early at page index {page_number}.")
                break
                
            collected_offers_metadata.extend(raw_offers)
            print(f"[PROGRESS] Successfully stored metadata for {len(raw_offers)} entries from index page {page_number}.")
            
        print(f"\n[PHASE 1 FINISHED] Harvested {len(collected_offers_metadata)} base properties URLs metadata.")
        
        # PHASE 2: INSPECT DEEP PROPERTY PAGES INDIVIDUALLY
        print(f"\n--- PHASE 2: Initializing Deep Subpage Scraper for {len(collected_offers_metadata)} elements ---")
        for index, offer in enumerate(collected_offers_metadata, start=1):
            title = offer.get('name', 'N/A').strip()
            price = offer.get('price', 'N/A')
            link = offer.get('url', 'N/A')
            
            price_spec = offer.get('priceSpecification', {})
            price_per_m = price_spec.get('price', 'N/A')
            
            print(f"\nProcessing queue item [{index}/{len(collected_offers_metadata)}]")
            
            if not link or link == 'N/A':
                print("[SKIP] Broken URL configuration string parsed.")
                continue
                
            # Perform granular page extraction routing 
            deep_details = fetch_detailed_property_data(driver, link)
            
            complete_row = {
                'Title': title,
                'Total Price (PLN)': price if isinstance(price, (int, float)) else 'N/A',
                'Price per SQM (PLN)': price_per_m if isinstance(price_per_m, (int, float)) else 'N/A',
                'Rooms': deep_details['Rooms'],
                'Floor': deep_details['Floor'],
                'Build Year': deep_details['Build Year'],
                'Ownership': deep_details['Ownership'],
                'URL': link,
                'Description': deep_details['Description']
            }
            
            compiled_dataset.append(complete_row)
            
        # PHASE 3: FILE IO STORAGE STREAMPERSISTENCE
        save_dataset_to_csv(compiled_dataset, OUTPUT_FILE_PATH)
            
    except Exception as critical_error:
        print(f"[FATAL ERROR] Pipeline master loop crashed: {critical_error}")
    finally:
        if 'driver' in locals():
            print("Terminating active automation Chrome worker node environment...")
            driver.quit()