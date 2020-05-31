"""
build_birb_list.py

A simple script to retrieve all of the birb data necessary.

"""


import base64
import shutil
import os
import re
import uuid
import json
from bs4 import BeautifulSoup
import requests

BIRBS_DIR = "../birbs/"
BIRBS_FILE = "birbs.json"
BASE_URL = "https://wikipedia.org"
ARTICLE_URL = "/wiki/List_of_birds_of_Newfoundland_and_Labrador"

r = requests.get(f"{BASE_URL}{ARTICLE_URL}")
soup = BeautifulSoup(r.text, "html.parser")

birbs_page = soup.find("div", class_="mw-parser-output")

def get_birb_image(link, uuid):
    # First visit the birbs wiki page
    r = requests.get(link)
    soup = BeautifulSoup(r.text, "html.parser")
    relative_thumbnail_link = (
        soup.find("a", class_="image").get("href").replace("wiki/", "")
    )
    thumbnail_link = f"{link}#media{relative_thumbnail_link}.jpg"

    r = requests.get(thumbnail_link)
    soup = BeautifulSoup(r.text, "html.parser")
    full_size_link = soup.find("meta", property="og:image").get("content")

    response = requests.get(full_size_link, stream=True)
    with open(os.path.join(BIRBS_DIR, f"{uuid}.jpg"), "wb+") as out_file:
        shutil.copyfileobj(response.raw, out_file)
        del response

    return str(os.path.join(BIRBS_DIR, f"{uuid}.jpg"))


with open(BIRBS_FILE, "w") as f:
    birbs_data = {}
    birb_list = []

    for birb in birbs_page.find_all("li"):

        link = birb.find("a")

        thumbnail = f"https:{birbs_page.find('img').get('src')}"
        name = birb.text.split(",")[0]

        if (
            not link
            or re.search(r"(\^|^[a-zA-Z0-9]{1}$)", name)
            or re.search(r"(\#|(List_of_birds))", link.get("href"))
        ):
            continue

        link = f"{BASE_URL}{link.get('href')}"
        print(f"Working on {link}")

        birb_uuid = str(uuid.uuid4())
        birb_image_path = get_birb_image(link, birb_uuid)

        r = requests.get(link)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", class_="infobox biota")

        items = table.find_all("tr")

        binomial_name = table.find("span", class_="binomial").text

        details = [list(filter(None, item.text.split("\n"))) for item in items]
        details = [item for item in details if len(item) > 1]

        for pair in details:
            pair[0] = pair[0].replace(":", "").lower()

        try:
            details = details[2:7]
            details[-1][-1] = details[-1][-1].replace("\xa0", " ")
            details = dict(details)
        except ValueError:
            print("Couldn't parse that bird!")
            continue

        birb_list.append(
            {
                "name": name,
                "binomial_name": binomial_name,
                "details": details,
                "link": link,
                "uuid": birb_uuid,
            }
        )

    birbs_data.update({"birbs": birb_list})

    json.dump(birbs_data, f)
