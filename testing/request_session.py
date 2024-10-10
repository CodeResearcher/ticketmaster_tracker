import requests

session = requests.Session()
session.headers.update({
    "cookie": "eps_sid=XXX; BID=XXX; reese84=XXX; SID=XXX; sticky=XXX",
    "referer": "https://www.ticketmaster.co.uk/api/quickpicks/XXX/list?resale=true&qty=1&offset=0&limit=100&sort=price",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "de-DE,de;q=0.9",
    "Connection": "keep-alive",
    "DNT": "1",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "Priority": "u=0, i",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-ch-ua-platform": "Windows",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua": "Chromium;v=128,Not;A=Brand;v=24,Google Chrome;v=128"
})
response = session.get("https://www.ticketmaster.co.uk/api/quickpicks/XXX/list?resale=true&qty=1&offset=0&limit=100&sort=price")
print(response.status_code)