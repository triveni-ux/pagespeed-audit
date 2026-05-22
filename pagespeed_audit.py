import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import cloudscraper

# 🔑 API Key
api_key = "AIzaSyDjs-ppllZ8Kp2T5_uqrAuUApgU3oHz4PI"

# 📅 Date
date = datetime.now().strftime("%d_%m_%Y")

# 📄 Sitemap URLs
sitemap_urls = [
    "https://nextagile.ai/sitemap_index.xml",
    "https://nextagile.ai/blogs/sitemap_index.xml"
]

# ☁️ Cloudflare scraper
scraper = cloudscraper.create_scraper()

# 📊 Results
results = []

# 🎯 Extract URLs from sitemap
def extract_urls_from_sitemap(sitemap_url):

    urls = []

    try:

        response = scraper.get(
            sitemap_url,
            timeout=30
        )

        if response.status_code != 200:
            return urls

        soup = BeautifulSoup(response.text, "xml")

        # 🔁 Sitemap Index
        if soup.find_all("sitemap"):

            sitemap_links = [
                loc.text.strip()
                for loc in soup.find_all("loc")
            ]

            for sm_url in sitemap_links:

                try:

                    sm_response = scraper.get(
                        sm_url,
                        timeout=30
                    )

                    sm_soup = BeautifulSoup(
                        sm_response.text,
                        "xml"
                    )

                    child_urls = [
                        loc.text.strip()
                        for loc in sm_soup.find_all("loc")
                    ]

                    urls.extend(child_urls)

                except:
                    pass

        # 📄 Normal sitemap
        else:

            urls = [
                loc.text.strip()
                for loc in soup.find_all("loc")
            ]

    except:
        pass

    return urls


# 🔁 Collect all URLs
all_urls = []

for sitemap in sitemap_urls:
    all_urls.extend(
        extract_urls_from_sitemap(sitemap)
    )

# 🧹 Remove duplicates
all_urls = list(set(all_urls))

# 🔍 Filter URLs
urls = [

    url for url in all_urls

    if (
        url.startswith("http")
        and not url.endswith(".jpg")
        and not url.endswith(".png")
        and not url.endswith(".jpeg")
        and not url.endswith(".webp")
        and not url.endswith(".gif")
        and not url.endswith(".pdf")
        and not url.endswith(".xml")
    )
]

print(f"✅ Total URLs Found: {len(urls)}")


# 🚀 Fetch PageSpeed
def fetch_pagespeed_scores(url):

    mobile_score = None
    desktop_score = None

    # 📱 Mobile
    try:

        mobile_api = (
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            f"?url={url}&strategy=mobile&key={api_key}"
        )

        mobile_res = requests.get(
            mobile_api,
            timeout=60
        )

        if mobile_res.status_code == 200:

            mobile_data = mobile_res.json()

            mobile_score = round(
                mobile_data["lighthouseResult"]["categories"]["performance"]["score"] * 100
            )

    except:
        pass

    # 🖥 Desktop
    try:

        desktop_api = (
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            f"?url={url}&strategy=desktop&key={api_key}"
        )

        desktop_res = requests.get(
            desktop_api,
            timeout=60
        )

        if desktop_res.status_code == 200:

            desktop_data = desktop_res.json()

            desktop_score = round(
                desktop_data["lighthouseResult"]["categories"]["performance"]["score"] * 100
            )

    except:
        pass

    return {
        "URL": url,
        "Mobile Performance Score": mobile_score,
        "Desktop Performance Score": desktop_score
    }


# 🚀 Run audits
with ThreadPoolExecutor(max_workers=5) as executor:

    futures = [
        executor.submit(fetch_pagespeed_scores, url)
        for url in urls
    ]

    for future in as_completed(futures):
        results.append(future.result())


# 📄 Create DataFrame
df = pd.DataFrame(results)

# 🔢 Convert numeric
df["Mobile Performance Score"] = pd.to_numeric(
    df["Mobile Performance Score"],
    errors="coerce"
)

df["Desktop Performance Score"] = pd.to_numeric(
    df["Desktop Performance Score"],
    errors="coerce"
)

# ❌ Remove failed rows
df = df.dropna()

# 📊 Sort
df = df.sort_values(
    by="Mobile Performance Score",
    ascending=True
)

# 💾 Save Excel
file_name = f"pagespeed_report_{date}.xlsx"

df.to_excel(
    file_name,
    index=False,
    engine="xlsxwriter"
)

print("✅ Report Generated")
