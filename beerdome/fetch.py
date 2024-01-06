import sys, os

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import time
import requests
from bs4 import BeautifulSoup
import cfscrape
import configparser

from database import (
    select_from_beers,
    check_if_exists,
    create_beer,
    set_untappd_urls,
    set_skip,
    db_close,
)
from untappd import get_untappd_styles, get_missing_styles

config = configparser.ConfigParser()
config.read("settings.ini")
shop = int(config["BEERDOME"]["shopId"])

scraper = cfscrape.create_scraper()

headers = {"User-Agent": config["GENERAL"]["userAgent"]}
pages = ["all-beers", "sale"]


def get_beers_from_shop(index=None, beers={}, pages_index=0):
    url = f'{config["BEERDOME"]["baseURL"]}/{pages[pages_index]}/?format=json'
    if index:
        url = f'{config["BEERDOME"]["baseURL"]}/{pages[pages_index]}/page{index}.html?format=json'

    r = requests.get(url, headers=headers)
    data = r.json()["collection"]
    products = data["products"]
    beers.update(products)

    if data["page"] < data["pages"]:
        get_beers_from_shop(data["page_next"], pages_index=pages_index)
    elif data["page"] == data["pages"]:
        new_pages_index = pages_index + 1

        if new_pages_index >= len(pages):
            return

        get_beers_from_shop(None, pages_index=new_pages_index)

    return beers


def get_links_from_shop():
    print("Getting individual beer-urls")

    all_beers = get_beers_from_shop()

    for key in all_beers:
        beer_id_shop = all_beers[key]["id"]
        url_site = f'{config["BEERDOME"]["baseURL"]}/{all_beers[key]["url"]}'

        exists = check_if_exists(beer_id_shop, shop)

        if not exists:
            create_beer(beer_id_shop, url_site, shop)


def get_beer_details():
    print("Geting Untappd-urls")

    beers = select_from_beers("beer_id_shop, url_site, untappd_url, skip")

    for beer_id_shop, url_site, untappd_url, skip in beers:
        if not untappd_url and not skip:
            url = f"{url_site}?format=json"

            r = requests.get(url, headers=headers)
            beer = r.json()["product"]
            if beer["specs"]:
                has_untapp_link = any(
                    "Untappd" in d.values() for d in beer["specs"].values()
                )

                if has_untapp_link:
                    for key in beer["specs"]:
                        if beer["specs"][key]["title"] == "Untappd":
                            html = beer["specs"][key]["value"]
                            soup = BeautifulSoup(html, "html.parser")
                            untappd_url = soup.find("a")["href"]

                            if "untappd.com/" in untappd_url:
                                set_untappd_urls(untappd_url, beer_id_shop, shop)
                            else:
                                set_skip(beer_id_shop, shop)
            else:
                set_skip(beer_id_shop, shop)

            time.sleep(int(config["GENERAL"]["sleepTime"]))


print("Getting beers")
get_beers_from_shop()
get_links_from_shop()
get_beer_details()
get_untappd_styles()
get_missing_styles()

db_close()
