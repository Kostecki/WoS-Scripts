import time
from bs4 import BeautifulSoup
import cfscrape
import configparser

from database import select_from_beers, set_style

config = configparser.ConfigParser()
config.read("settings.ini")

scraper = cfscrape.create_scraper()

CID = config["UNTAPPD"]["clientId"]
CS = config["UNTAPPD"]["clientSecret"]
AT = config["UNTAPPD"]["accessToken"]

headers = {"User-Agent": config["GENERAL"]["userAgent"]}


def get_untappd_styles():
    print("Getting styles from Untappd")

    beers = select_from_beers("beer_id_shop, untappd_url, style, shop")

    for beer_id_shop, untapd_url, style, shop in beers:
        if untapd_url and not style:
            r = scraper.get(untapd_url, headers=headers)
            soup = BeautifulSoup(r.content, "html.parser")
            the_style = soup.select_one(".style").get_text()

            set_style(the_style, beer_id_shop, shop)

            time.sleep(int(config["UNTAPPD"]["sleepTime"]))


def get_missing_styles():
    print("\nAvailable missing styles")
    url = f"https://api.untappd.com/v4/badges/styles_not_had?client_id={CID}&client_secret={CS}&access_token={AT}"
    r = scraper.get(url, headers=headers)
    styles = r.json()["response"]["items"]

    beers = select_from_beers("url_site, style")
    style_list = [d["style_name"] for d in styles]

    styles = {}

    for url_site, style in beers:
        if style and style in style_list:
            if style in styles:
                styles[style].append(url_site)
            else:
                styles[style] = [url_site]

    for style in styles:
        print(f"\n{style}")
        for link in styles[style]:
            print(link)
