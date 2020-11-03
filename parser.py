import requests
from bs4 import BeautifulSoup
import csv
import os

URL = "https://auto.ria.com/uk/newauto/marka-jeep/"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36", "accept": "*/*"}
HOST = "https://auto.ria.com/uk"
FILE = "cars.csv"


def get_html(url, params=None):
    req = requests.get(url, headers=HEADERS, params=params)
    return req


def get_pages_count(html):
    soap = BeautifulSoup(html, 'html.parser')
    pagination = soap.find_all('span', class_="mhide")
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1


def get_content(html):
    soap = BeautifulSoup(html, 'html.parser')
    items = soap.find_all(
        'div', class_="proposition_area")
    cars = []
    for item in items:
        uah_price = item.select_one('span.grey.size13')
        if uah_price:
            uah_price = uah_price.get_text()
        else:
            uah_price = 'Уточніть ціну'
        cars.append({
            'title': item.find('h3').get_text(strip=True),
            'url': HOST+item.find('a').get('href'),
            'usd_price': item.find('span', class_="green").get_text(strip=True),
            'uah_price': uah_price,
            'city': item.select_one('div.proposition_region strong').get_text(strip=True),
        })
    # print(cars)
    return cars


def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Title', 'Link', 'Price USA', 'Price UAH', 'City'])
        for item in items:
            writer.writerow([item['title'], item['url'],
                             item['usd_price'], item['uah_price'], item['city']])


def parse():
    URL = input("Enter url: ").strip()
    html = get_html(URL)
    if html.status_code == 200:
        # print(get_content(html.text))
        cars = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count+1):
            print(f"Parse page number {page} on {pages_count}")
            html = get_html(URL, params={'page': page})
            cars.extend(get_content(html.text))
        save_file(cars, FILE)
        print(f"Take {len(cars)} cars.")
        os.startfile(FILE)
    else:
        print("Error!")


parse()
