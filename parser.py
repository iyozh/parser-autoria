import os

import requests
from bs4 import BeautifulSoup
import csv
import subprocess

HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}

HOST = "https://avto.ria.com"
PATH = "cars.csv"


def get_html(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)
    return response


def get_content(html):
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all("div", class_="proposition")
    cars = []
    for item in items:
        cars.append(
            {
                "title": item.find("div", class_="proposition_title").get_text(
                    strip=True
                ),
                "link": HOST + item.find("a", class_="proposition_link").get("href"),
                "photo": item.find("div", class_="photo-car").find("img").get("src"),
                "USD": item.find("span", class_="green").get_text(strip=True),
                "UAH": item.find("span", class_="grey size13").get_text(strip=True),
                "city": item.find("div", class_="proposition_region size13")
                .find_next("strong")
                .get_text(strip=True),
            }
        )
    return cars


def pages_count(html):
    soup = BeautifulSoup(html, "html.parser")
    pagination = soup.find_all("span", class_="page-item mhide")
    return int(pagination[-1].get_text())


def parse():
    url = input("Введите URL:").strip()
    html = get_html(url)
    if not html.status_code == 200:
        return print("Error")
    pages = pages_count(html.text)
    cars = []
    for page in range(1, pages + 1):
        html = get_html(url, params={"page": page})
        cars.extend(get_content(html.text))
    save_data(cars, PATH)


def save_data(data, path):
    with open(path, "w", newline="") as fp:
        writer = csv.writer(fp, delimiter=";")
        writer.writerow(["Brend", "Link", "USD", "UAH", "City", "Image"])
        for item in data:
            writer.writerow(
                [
                    item["title"],
                    item["link"],
                    item["USD"],
                    item["UAH"],
                    item["city"],
                    item["photo"],
                ]
            )
            image = get_html(item["photo"])
            name = item["photo"].split("/")[-1]
            with open(f"img/{name}", "wb") as fp:
                fp.write(image.content)


parse()
