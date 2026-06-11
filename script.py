import requests
from bs4 import BeautifulSoup

url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa/warszawa/warszawa"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Upgrade-In-Transformation": "1",
    "Connection": "keep-alive"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("Connected!")
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find_all('p', attrs={"data-cy": "listining-item-title"})

    print(f"Found {len(title)} ads on the site.")
    for title in titles:
        print(title.text)
else:
    print(f"Connection error: {response.status_code}")