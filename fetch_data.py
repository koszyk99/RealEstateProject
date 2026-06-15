import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

# target URL
url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa/warszawa/warszawa"

print("Launching Undetected Chrome via Selenium...")

# configure undetected chrome options
options = uc.ChromeOptions()
options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

try:
    # launch uc browser
    driver = uc.Chrome(options=options, headless=False)

    print(f"Entering the site: {url}")
    driver.get(url)

    # wait for the page to fully load dynamic content
    print("I'm waiting for the page...")
    time.sleep(7)

    # save a screenshot and HTML source for debugging 
    driver.save_screenshot("page_view.png")
    with open("page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Save page_view.png and page.html to project folder.")

    # extract HTML source after the page loads
    html_source = driver.page_source
    # parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_source, 'html.parser')

    # find all listings titles using the data-cy attribute
    listings = soup.find_all('article', attrs={"data-cy": "listing-item"})

    print("-" * 30)
    print(f"Success! Found {len(listings)} on the site.")
    print("-" * 30)

    # print each title text
    for item in listings:
        # obtain the title
        title_tag = item.find('p', attrs={"data-cy": "listing-item-title"})
        title = title_tag.text.strip() if title_tag else "No title found."

        # obtain total price
        price_tag = item.find('span', attrs={"data-cy": "listing-item-price"})
        price = price_tag.text.strip() if price_tag else "No price found."

        # obtain price per meter
        price_per_m_tag = item.find('span', class_=lambda c: c and 'css-19v76f8' in c)
        if not price_per_m_tag:
            # alternative search for text containing "zł/m²"
            price_per_m_tag = item.find(string=lambda text: text and "zł/m²" in text)

        price_per_m = price_per_m_tag.strip() if price_per_m_tag else "No information found."

        # extract the link to the advertisement
        link_tag = item.find('a', attrs={"data-cy": "listing-item-link"})
        href = link_tag['href'] if link_tag else ""

        # Ototdom sometimes privides relative links (pl/oferta/...), you need to add a domain
        full_link = f"https://www.otodom.pl{href}" if href.startswith('/') else href

        # display a formatted set of data in the console
        print(f"TITLE: {title}")
        print(f"PRICE: {price}")
        print(f"LINK: {price} ({price_per_m})")
        print("-" * 50)

except Exception as e:
    # catch any running errors
    print(f"An error occurred: {e}")

finally:
    # ensure the browser is closed even if an error ocured
    if 'driver' in locals():
        print("Closing the browser...")
        driver.quit()