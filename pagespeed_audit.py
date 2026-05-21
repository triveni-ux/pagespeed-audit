import pandas as pd
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 🔑 API Key
api_key = "AIzaSyDjs-ppllZ8Kp2T5_uqrAuUApgU3oHz4PI"

# 📅 Date
date = datetime.now().strftime("%d_%m_%Y")

# 📄 URLs
urls = [
"https://nextagile.ai/sitemap_index.xml",
  "https://nextagile.ai/blogs/sitemap_index.xml"
]

results = []

# 🚀 Function
def fetch_pagespeed_scores(url):

    mobile_score = None
    desktop_score = None

    try:

        mobile_api = (
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            f"?url={url}&strategy=mobile&key={api_key}"
        )

        mobile_res = requests.get(mobile_api, timeout=60)

        if mobile_res.status_code == 200:

            mobile_data = mobile_res.json()

            mobile_score = round(
                mobile_data["lighthouseResult"]["categories"]["performance"]["score"] * 100
            )

    except:
        pass

    try:

        desktop_api = (
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            f"?url={url}&strategy=desktop&key={api_key}"
        )

        desktop_res = requests.get(desktop_api, timeout=60)

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

# 🚀 Run
with ThreadPoolExecutor(max_workers=5) as executor:

    futures = [
        executor.submit(fetch_pagespeed_scores, url)
        for url in urls
    ]

    for future in as_completed(futures):
        results.append(future.result())

# 📄 Save Excel
df = pd.DataFrame(results)

file_name = f"pagespeed_report_{date}.xlsx"

df.to_excel(
    file_name,
    index=False,
    engine="xlsxwriter"
)

print("✅ Report Generated")
