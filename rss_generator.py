import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import os, re

URL = "https://fightnews.info/news"
BASE = "https://fightnews.info"
OUTPUT_PATH = "docs/fightnews.xml"

def fetch_articles():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    items = []
    for block in soup.select("div.row.post-list"):
        a = block.select_one("a.page-title")
        if not a:
            continue
        title = a.get_text(strip=True)
        link = BASE + a.get("href")
        desc_block = block.select_one(".col-lg-8")
        description = desc_block.get_text(" ", strip=True) if desc_block else ""
        hint = block.select_one(".hint")
        pub_date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
        if hint:
            m = re.search(r"(\d{1,2}:\d{2})", hint.get_text())
            if m:
                pub_date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

        items.append({
            "title": title,
            "link": link,
            "description": description,
            "pubDate": pub_date
        })
    return items

def create_rss(items):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "FightNews — Новости бокса"
    ET.SubElement(channel, "link").text = URL
    ET.SubElement(channel, "description").text = "Автообновляемая лента с fightnews.info"
    ET.SubElement(channel, "language").text = "ru"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    for it in items:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = it["title"]
        ET.SubElement(item, "link").text = it["link"]
        ET.SubElement(item, "description").text = it["description"]
        ET.SubElement(item, "pubDate").text = it["pubDate"]
        ET.SubElement(item, "guid").text = it["link"]

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    ET.ElementTree(rss).write(OUTPUT_PATH, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    articles = fetch_articles()
    create_rss(articles)
