import sys
import configparser
import mariadb

config = configparser.ConfigParser()
config.read("settings.ini")

try:
    conn = mariadb.connect(
        user=config["DB"]["username"],
        password=config["DB"]["password"],
        host=config["DB"]["host"],
        port=int(config["DB"]["port"]),
        database=config["DB"]["database"],
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()


def select_from_beers(fields):
    cur.execute(f"SELECT {fields} from beers")
    row = cur.fetchall()

    return row


def check_if_exists(beer_id_shop, shop):
    cur.execute(
        "SELECT * FROM beers where beer_id_shop = ? AND shop = ?", (beer_id_shop, shop)
    )
    row = cur.fetchone()

    return row


def create_beer(beer_id_shop, url_site, shop, untappd_url=None):
    try:
        cur.execute(
            "INSERT INTO beers (beer_id_shop, url_site, shop, untappd_url) VALUES (?,?,?,?)",
            (beer_id_shop, url_site, shop, untappd_url),
        )
    except mariadb.Error as e:
        print(f"create_beer, Error: {e}")

    conn.commit()


def set_untappd_urls(untappd_url, beer_id_shop, shop):
    try:
        cur.execute(
            "UPDATE beers SET untappd_url = ? WHERE beer_id_shop = ? AND shop = ?",
            (untappd_url, beer_id_shop, shop),
        )
    except mariadb.Error as e:
        print(f"set_untappd_urls, Error: {e}")

    conn.commit()


def set_style(the_style, beer_id_shop, shop):
    try:
        cur.execute(
            "UPDATE beers SET style = ? WHERE beer_id_shop = ? AND shop = ?",
            (the_style, beer_id_shop, shop),
        )
    except mariadb.Error as e:
        print(f"set_style, Error: {e}")

    conn.commit()


def set_skip(beer_id_shop, shop):
    try:
        cur.execute(
            "UPDATE beers SET skip = ? WHERE beer_id_shop = ? AND shop = ?",
            (1, beer_id_shop, shop),
        )
    except mariadb.Error as e:
        print(f"set_skip, Error: {e}")

    conn.commit()


def db_close():
    conn.close()
