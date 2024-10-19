import os.path
import datetime
import json
import subprocess

import requests
from netscape_cookies import save_cookies_to_file

from libs.ticketmaster_toolkit import ticketmaster_toolkit
from libs.headless_browser import headless_browser

tm = ticketmaster_toolkit()
hb = headless_browser()

loop_enabled = True
failed_events = []
expires = []
header_dict = {}
for h in tm.header_list:
    header_dict.update(h)
response_status = 0
previous_status = 200

print("initialize cookie session...\r")

#open new tab to retrieve cookies
subprocess.Popen([tm.firefox_executable, "-new-tab", "https://www" + tm.domain])

#wait for new cookies available
tm.wait(tm.refresh_delay)

#load cookies
cookie_container = tm.get_cookie_container()

while loop_enabled:

    for e in tm.primary_events:

        url = "https://www" + tm.domain + tm.api_path + "{event}/".format(event = e) + tm.method
        data = {}
        
        if tm.selenium == "chrome":
            source = hb.setup_chrome(url)

        elif tm.selenium == "firefox":
            source = hb.setup_firefox(header_dict, url)

        if tm.selenium == None or tm.selenium == "":
            
            session = requests.Session()
            session.headers.update(header_dict)

            #load response JSON from file
            if tm.response_sample != None and os.path.isfile(tm.response_sample) == True:
                with open(tm.response_sample, 'r') as file:
                    data = json.load(file)
                tm.save_pick(e, data)

            #use cookie string
            elif ";" in tm.cookies:
                session.headers.update({"cookie": tm.cookies})
                response = session.get(url)
                response_status = response.status_code

            #use cookie container
            else:
                name_length = 0
                for c in cookie_container:
                    if name_length < len(c.name):
                        name_length = len(c.name)

                expires = [
                    f"{'Cookie' : <{name_length + 1}}{'Expires' : <19} Domain", 
                    f"{'------' : <{name_length + 1}}{'-------' : <19} ------"
                ]
                for c in cookie_container:
                    if c.expires != None:
                        expires.append(f"{c.name : <{name_length + 1}}{datetime.datetime.fromtimestamp(c.expires).strftime('%H:%M:%S %d.%m.%Y')} {c.domain}")

                response = session.get(url, cookies=cookie_container)
                response_status = response.status_code

            tm.show_trace(response_status, e, failed_events, expires)

            #load JSON response from request
            if response_status == 200:
                previous_status = response_status
                data = response.json()
                tm.save_pick(e, data)
                if 'eventId' in data:
                    del data['eventId']
                data['status'] = response_status
                #save_cookies_to_file(session.cookies, "cookies_extract.txt")

            #load new tab to refresh cookies
            elif response_status == 401: #and previous_status != 401:
                previous_status = response_status
                data = tm.set_default_attributes(data, response_status)
                print("load new cookie session...\r")
                subprocess.Popen([tm.firefox_executable, "-new-tab", "https://www" + tm.domain])
                tm.wait(tm.refresh_delay)
                cookie_container = tm.get_cookie_container()
                print("cookies loaded successfully!")

            #removes event if request timeout is reached
            elif response_status == 503 or response_status == 504:
                data = tm.set_default_attributes(data, response_status)
                tm.primary_events.remove(e)
                failed_events.append(e)
                if len(tm.secondary_events) > 0:
                    tm.primary_events.append(tm.secondary_events[0])
                    tm.secondary_events.pop(1)

            #cancel execution
            elif response_status != 0:
                f = open(os.path.join("logs", "{event}.html".format(event = e)), "w")
                f.write(response.text)
                f.close()
                loop_enabled = False
                break

        #load JSON response from Selenium
        else:
            hb.convert_source_to_json(source)
        
        tm.log_results(e, data)
        tm.wait(tm.request_delay)