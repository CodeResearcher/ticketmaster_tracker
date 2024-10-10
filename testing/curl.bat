curl "https://www.ticketmaster.co.uk/api/quickpicks/XXX/list?resale=true&qty=1&offset=0&limit=100&sort=price" ^
  -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7" ^
  -H "accept-language: de-DE,de;q=0.9" ^
  -H "cache-control: no-cache" ^
  -H "cookie: eps_sid=XXX; sticky=XXX; SID=XXX; BID=XXX; reese84=XXX" ^
  -H "dnt: 1" ^
  -H "pragma: no-cache" ^
  -H "priority: u=0, i" ^
  -H "referer: https://www.ticketmaster.co.uk/api/quickpicks/XXX/list?resale=true&qty=1&offset=0&limit=100&sort=price" ^
  -H ^"sec-ch-ua: ^\^"Chromium^\^";v=^\^"128^\^", ^\^"Not;A=Brand^\^";v=^\^"24^\^", ^\^"Google Chrome^\^";v=^\^"128^\^"^" ^
  -H "sec-ch-ua-mobile: ?0" ^
  -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^" ^
  -H "sec-fetch-dest: document" ^
  -H "sec-fetch-mode: navigate" ^
  -H "sec-fetch-site: same-origin" ^
  -H "upgrade-insecure-requests: 1" ^
  -H "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
  >> echos >> .\event_log.json