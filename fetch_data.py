import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa/warszawa/warszawa"

print("Launching Chromium via Selenium...")

# configuration uc
options = uc.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

try:
    # launch Chrome engine
    driver = uc.Chrome(options=options)

    print(f"Entering the site: {url}")
    driver.get(url)

    # waiting 7 seconds to load site
    print("I'm waiting for the page to load.")
    time.sleep(7)

    driver.save_screenshot("page_view.png")
    with open("page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Save page_view.png and page.html to project folder.")

    # load html
    html_source = driver.page_source
    # pass the code to BeautifulSoup
    soup = BeautifulSoup(html_source, 'html.parser')

    # we are trying to find the title of the advertisement
    titles = soup.find_all('p', attrs={"data-cy": "listing-item-title"})

    print("-" * 30)
    print(f"Success! Found {len(titles)} on the site.")
    print("-" * 30)

    for title in titles:
        print(title.text)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if 'driver' in locals():
        print("Closing the browser...")
        driver.quit()