import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://www.shl.com/solutions/products/product-catalog/"

headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(BASE_URL, headers=headers)

print("Status Code:", response.status_code)

html = response.text

# save raw page for debugging
with open("page.html", "w", encoding="utf-8") as f:
    f.write(html)

soup = BeautifulSoup(html, "html.parser")

assessments = []

# find all links
links = soup.find_all("a")

for link in links:

    text = link.get_text(strip=True)
    href = link.get("href")

    # keep only actual assessment pages
    if href and "/products/product-catalog/view/" in href and len(text) > 3:

        # remove unwanted entries
        unwanted = ["next", "learn more", "products", "assessments"]

        if text.lower() in unwanted:
            continue

        # make full URL
        if href.startswith("http"):
            full_url = href
        else:
            full_url = "https://www.shl.com" + href

        assessments.append({"name": text, "url": full_url})

# remove duplicates
unique = []
seen = set()

for item in assessments:

    if item["url"] not in seen:

        seen.add(item["url"])

        unique.append(item)

# save catalog
with open("catalog.json", "w", encoding="utf-8") as f:
    json.dump(unique, f, indent=2)

print("Saved", len(unique), "clean assessments")
