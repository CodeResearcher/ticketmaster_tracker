import sys
import os.path
import time
import datetime
import json
from json import JSONEncoder
import csv
from bs4 import BeautifulSoup
import subprocess

import requests
import http.cookiejar
import browser_cookie3
from netscape_cookies import save_cookies_to_file

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

class DateTimeEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()

def load_config(key, config):
    return config[key] if key in config else None

def does_id_exist(tickets, id):
    return any(pick['id'] == id for pick in tickets['picks'])

def get_cookie_container(cookie_list, domain):
    cookie_dict = {}
    for i in range(0, len(cookie_list)):
        if cookie_list[i]['domain'] == domain:
            cookie_dict[cookie_list[i]['name']] = cookie_list[i]['value']
    return requests.utils.cookiejar_from_dict(cookie_dict)

def set_defaults(e, data, status):
    if os.path.isfile("trackingg_history.csv") == True:
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
                d['isoDate'] = datetime.datetime.now()
                tickets['picks'].append(d)
        with open(directory, 'w', encoding='utf-8') as f:
            json.dump(tickets, f, ensure_ascii=False, indent=4, cls=DateTimeEncoder)

def write_log(e, data):
    if data != None and 'status' in data:
        data['eventId'] = e
        
        #write to JSON Lines File
        if 'date' in data:
            del data['date']
            del data['time']
        data['isoDate'] = datetime.datetime.now()
        json_directory = os.path.join("logs", "tracking_history.jsonl")
        with open(json_directory, 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, cls=DateTimeEncoder)
            f.write('\n')

        #write to CSV File
        if 'isoDate' in data:
            del data['isoDate']
        data['time'] = datetime.datetime.now().strftime("%H:%M:%S")
        data['date'] = datetime.datetime.now().strftime("%d.%m.%Y")
        csv_directory = os.path.join("logs", "tracking_history.csv")
        file_exists = os.path.isfile(csv_directory)
        f = open(csv_directory, 'a', newline='\n')
        csv_writer = csv.writer(f, delimiter=',', quotechar="'")
        if file_exists == False:
            csv_writer.writerow(data.keys())
        csv_writer.writerow(data.values())
        f.close()

def wait(delay):
    for remaining in range(delay, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d}s until execution continues...".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
    print("\r")

#load initial configuration
with open('config.json', 'r') as file:
    config = json.load(file)

#Headless Browser
selenium = load_config("selenium", config)
#Ticketmaster Cookie
cookies = load_config("cookies", config)
#Ticketmaster Domain
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
header_dict = {}
for h in header_list:
    header_dict.update(h)
response_status = 0
previous_status = 200

print("initialize cookie session...\r")

#open new tab to retrieve cookies
subprocess.Popen([firefox_executable, "-new-tab", "https://www" + domain])
wait(refresh_delay)

#load cookies
if os.path.splitext(cookies)[1] == ".txt":
    cookie_container = http.cookiejar.MozillaCookieJar()
    cookie_container.load(cookies)
else:
    cookie_container = browser_cookie3.firefox(domain_name=domain)
cookie_dict = requests.utils.dict_from_cookiejar(cookie_container)

while loop_enabled:

    for e in primary_events:

        data = {}

        url = "https://www" + domain + api_path + "{event}/".format(event = e) + load_config("method", config)
        now = datetime.datetime.now()
        
        if selenium == "chrome":

            #https://developer.chrome.com/docs/chromedriver/downloads
            s = Service('.venv\chromedriver.exe')

            chrome_options = webdriver.ChromeOptions()
            #chrome_options.add_argument("–disable-extensions")
            #chrome_options.add_argument("–headless")
            chrome_options.add_argument("start-maximized")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
            chrome_options.add_experimental_option("useAutomationExtension", False) 
            #chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9111")

            driver = webdriver.Chrome(service=s, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")      
            driver.get(url)
            source = driver.page_source
            print(driver.title)

        elif selenium == "firefox":

            #https://github.com/mozilla/geckodriver/releases
            s = webdriver.FirefoxService('.venv\geckodriver.exe')

            user_agent = header_dict['User-Agent']
            profile = FirefoxProfile()
            profile.set_preference("general.useragent.override", user_agent)
            profile.set_preference("javascript.enabled", True)
            default_preferences = profile.DEFAULT_PREFERENCES

            firefox_options = webdriver.FirefoxOptions()
            firefox_options.headless = True
            firefox_options.profile = profile

            #driver = webdriver.Firefox(service=s, service_args=['--marionette-port', '2828', '--connect_existing'])
            driver = webdriver.Firefox(service=s, options=firefox_options)
            driver.get(url)
            source = driver.page_source
            print(driver.title)

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
                    f"{'Cookie' : <10}{'Expires' : <19} Domain", 
                    f"{'------' : <10}{'-------' : <19} ------"
                ]
                for c in cookie_container:
                    if c.expires != None:
                        expires.append(f"{c.name : <10}{datetime.datetime.fromtimestamp(c.expires).strftime('%H:%M:%S %d.%m.%Y')} {c.domain}")
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
                print("load new cookie session...\r")
                subprocess.Popen([firefox_executable, "-new-tab", "https://www" + domain])
                wait(refresh_delay)
                cookie_container = browser_cookie3.firefox(domain_name=domain)
                print("cookies loaded successfully!")

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
            cookie_container = get_cookie_container(driver.get_cookies(), domain)
            driver.quit()
            soup = BeautifulSoup(source, 'html.parser')
            pre = soup.find_all('pre')[-1]
            pre_text = pre.text.strip()
            data = json.loads(pre_text)
            print(data)
        
        write_log(e, data)
        wait(load_config("request_delay", config))