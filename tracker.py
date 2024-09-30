import os.path
import time
import datetime
import json
import csv
from bs4 import BeautifulSoup
import subprocess
import requests
import http.cookiejar
from selenium import webdriver
import browser_cookie3
from netscape_cookies import save_cookies_to_file

def load_config(key, config):
    return config[key] if key in config else None

def does_id_exist(tickets, id):
    return any(pick['id'] == id for pick in tickets['picks'])

def set_defaults(e, data, status):
    if os.path.isfile("{event}.csv".format(event = e)) == True:
        data['quantity'] = 0
        data['total'] = 0
        data['picks'] = []
        data['descriptions'] = []
        data['status'] = status
        #data['cookies'] = None
        #data['expires'] = None
    return data

def save_pick(event_id, data, picks_list):
    directory = os.path.join("logs", picks_list)
    if 'picks' in data and len(data['picks']) > 0:
        if os.path.isfile(directory) == True:
            with open(directory, 'r') as file:
                tickets = json.load(file)
        else:
            tickets = {"picks":[]}
        for d in data['picks']:
            if does_id_exist(tickets, d['id']) == False:
                d['eventId'] = event_id
                tickets['picks'].append(d)
        with open(directory, 'w', encoding='utf-8') as f:
            json.dump(tickets, f, ensure_ascii=False, indent=4)

def write_csv(e, data):
    if data != None:
        data['time'] = now.strftime("%H:%M:%S")
        data['date'] = now.strftime("%d.%m.%Y")
        file_exists = os.path.isfile("{event}.csv".format(event = e))
        directory = os.path.join("logs", "{event}.csv".format(event = e))
        f = open(directory, "a", newline='\n')
        csv_writer = csv.writer(f, delimiter=',', quotechar="'")
        if file_exists == False:
            csv_writer.writerow(data.keys())
        csv_writer.writerow(data.values())
        f.close()

#load initial configuration
with open('config.json', 'r') as file:
    config = json.load(file)

"""
possible values:
- chrome
- firefox
"""
selenium = load_config("selenium", config)

"""
possible values:
- cookies.txt
- "eps_sid=XXX; BID=XXX; reese84=XXX; SID=XXX; sticky=XXX"
"""
cookies = load_config("cookies", config)

domain = load_config("domain", config)

#API path
api_path = load_config("api_path", config)
#Headers
header_list = load_config("headers", config)
#array of primary event ids
primary_events = load_config("primary_events", config)
#array of secondary event ids
secondary_events = load_config("secondary_events", config)
#JSON file with sample response
response_sample = load_config("response_sample", config)
#JSON file with available picks
picks_list = load_config("picks_list", config)
#path to firefox executable
firefox_executable = load_config("firefox_executable", config)
#delay of next request after new cookies
refresh_delay = load_config("refresh_delay", config)

loop_enabled = True
cookie_delimiter = " | "
failed_events = []
expires = []
data = {}
header_dict = {}
for h in header_list:
    header_dict.update(h)
response_status = 0
previous_status = 200

#open new tab to retrieve cookies
subprocess.Popen([firefox_executable, "-new-tab", "https://www" + domain])
time.sleep(refresh_delay)

#load cookies
if os.path.splitext(cookies)[1] == ".txt":
    cookie_container = http.cookiejar.MozillaCookieJar()
    cookie_container.load(cookies)
else:
    cookie_container = browser_cookie3.firefox(domain_name=domain)
cookie_dict = requests.utils.dict_from_cookiejar(cookie_container)

while loop_enabled:

    for e in primary_events:

        url = "https://www" + domain + api_path + "{event}/".format(event = e) + load_config("method", config)
        now = datetime.datetime.now()
        
        if selenium == "chrome":

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("–disable-extensions")
            chrome_options.add_argument("–headless")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
            chrome_options.add_experimental_option("useAutomationExtension", False) 
            #chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9111")
            driver = webdriver.Chrome(options=chrome_options)

            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")      
            print(driver.title)
            driver.get(url)
            cookie_list = driver.get_cookies()
            cookie_dict = {}
            for i in range(0, len(cookie_list)):
                if cookie_list[i]['domain'] == domain:
                    cookie_dict[cookie_list[i]['name']] = cookie_list[i]['value']
            cookie_container = requests.utils.cookiejar_from_dict(cookie_dict)
            source = driver.page_source

        elif selenium == "firefox":

            driver = webdriver.Firefox(executable_path="", service_args=['--marionette-port', '2828', '--connect_existing'])
            print(driver.title)
            driver.get(url)
            cookie_container = driver.get_cookie()
            source = driver.page_source

        if selenium == None or selenium == "":
            
            session = requests.Session()
            session.headers.update(header_dict)

            #load response JSON from file
            if response_sample != None and os.path.isfile(response_sample) == True:
                with open(response_sample, 'r') as file:
                    data = json.load(file)
                save_pick(e, data, picks_list)

            #use cookie string
            elif ";" in cookies:
                session.headers.update({"cookie": cookies})
                response = session.get(url)
                response_status = response.status_code

            #use cookie container
            else:
                expires = [
                    f"{'Cookie' : <33}{'Expires' : <19} Domain", 
                    f"{'------' : <33}{'-------' : <19} ------"
                ]
                for c in cookie_container:
                    if c.expires != None:
                        expires.append(f"{c.name : <33}{datetime.datetime.fromtimestamp(c.expires).strftime('%H:%M:%S %d.%m.%Y')} {c.domain}")
                response = session.get(url, cookies=cookie_container)
                response_status = response.status_code

            #print status, execution time and expiration time per cookie
            print(
                f"\r\n{now.strftime('%H:%M:%S')} HTTP {str(response_status).strip()}" +
                f"\r\nCurrent Event: {e}" +
                f"\r\nFailed Events: {len(failed_events)}" +
                "\r\n" +
                "\r\n".join(i for i in expires)
            )

            #load JSON response from request
            if response_status == 200:
                previous_status = response_status
                data = response.json()
                save_pick(e, data, picks_list)
                if 'eventId' in data:
                    del data['eventId']
                data['status'] = response_status
                #data['cookies'] = cookie_delimiter.join('{}:{}'.format(key, value) for key, value in cookie_dict.items())
                #data['expires'] = cookie_delimiter.join(i for i in expires)
                #save_cookies_to_file(session.cookies, "cookies_extract.txt")

            #load new tab to refresh cookies
            elif response_status == 401: #and previous_status != 401:
                previous_status = response_status
                data = set_defaults(e, data, response_status)
                subprocess.Popen([firefox_executable, "-new-tab", "https://www" + domain])
                time.sleep(refresh_delay)
                cookie_container = browser_cookie3.firefox(domain_name=domain)

            #removes event if request timeout is reached
            elif response_status == 503 or response_status == 504:
                data = set_defaults(e, data, response_status)
                primary_events.remove(e)
                failed_events.append(e)
                if len(secondary_events) > 0:
                    primary_events.append(secondary_events[0])
                    secondary_events.pop(1)

            #cancel execution
            elif response_status != 0:
                f = open(os.path.join("logs", "{event}.html".format(event = e)), "w")
                f.write(response.text)
                f.close()
                loop_enabled = False
                break

        #load JSON response from Selenium
        else:
            soup = BeautifulSoup(source, 'html.parser')
            pre = soup.find_all('pre')[-1]
            pre_text = pre.text.strip()
            data = json.loads(pre_text)
        
        write_csv(e, data)
        time.sleep(load_config("request_delay", config))

#driver.quit()