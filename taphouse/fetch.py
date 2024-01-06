import sys, os

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import requests
from bs4 import BeautifulSoup
import configparser
import uuid

from database import check_if_exists, create_beer, db_close
from untappd import get_missing_styles, get_untappd_styles

config = configparser.ConfigParser()
config.read("settings.ini")
shop = int(config["TAPHOUSE"]["shopId"])

headers = {"User-Agent": config["GENERAL"]["userAgent"]}


def get_beers_from_shop():
    print("Scraping site for beers")

    url = config["TAPHOUSE"]["baseURL"]
    r = requests.get(url, headers)

    soup = BeautifulSoup(r.content, "html.parser")
    beer_table = soup.find("table", id="beerTable")
    table_body = beer_table.find("tbody")

    data = []
    rows = table_body.find_all("tr")
    for row in rows:
        data.append(row.find("a", attrs={"class", "untappdLink"})["href"])

    return data


def create_new_beers():
    print("Creating beers in DB")

    all_beers = get_beers_from_shop()

    for untappd_url in all_beers:
        id = uuid.uuid4().hex

        exists = check_if_exists(id, shop)

        if not exists:
            create_beer(id, config["TAPHOUSE"]["baseURL"], shop, untappd_url)


create_new_beers()
get_untappd_styles()
get_missing_styles()

db_close()
