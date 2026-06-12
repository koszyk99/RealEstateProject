import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

# target URL
url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa/warszawa/warszawa"

print("Launching Undetected Chrome via Selenium...")

# configure undetected chrome options
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

try:
    # launch uc browser
    driver = uc.Chrome(options=options)

    print(f"Entering the site: {url}")
    driver.get(url)

    # wait for the page to fully load dynamic content
    print("I'm waiting for the page.")
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
    titles = soup.find_all('p', attrs={"data-cy": "listing-item-title"})

    print("-" * 30)
    print(f"Success! Found {len(titles)} on the site.")
    print("-" * 30)

    # print each title text
    for title in titles:
        print(title.text)

except Exception as e:
    # catch any running errors
    print(f"An error occurred: {e}")

finally:
    # ensure the browser is closed even if an error ocured
    if 'driver' in locals():
        print("Closing the browser...")
        driver.quit()