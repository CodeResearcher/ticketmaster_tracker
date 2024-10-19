import sys
import os.path
import time
import datetime
from decimal import Decimal
import json
from json import JSONEncoder
import csv
import requests
import http.cookiejar
from http.cookiejar import CookieJar 
import browser_cookie3
import sqlite3
import subprocess
import winsound

class DateTimeEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()

class ticketmaster_toolkit:

    def __init__(self):
        with open('config.json', 'r') as file:
            self.config = json.load(file)

        #initialize SQLite database
        with open('init.sql', 'r') as file:
            sql_script = file.read()
        conn = sqlite3.connect('logs\data.db') 
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()
        conn.close()

        #Headless Browser
        self.selenium = self.load_config("selenium")
        #Ticketmaster Cookie
        self.cookies = self.load_config("cookies")
        #Ticketmaster Domain
        self.domain = self.load_config("domain")
        #API path
        self.api_path = self.load_config("api_path")
        #API method
        self.method = self.load_config("method")
        #Headers
        self.header_list = self.load_config("headers")
        #array of primary event ids
        self.primary_events = self.load_config("primary_events")
        #array of secondary event ids
        self.secondary_events = self.load_config("secondary_events")
        #JSON file with sample response
        self.response_sample = self.load_config("response_sample")
        #path to firefox executable
        self.firefox_executable = self.load_config("firefox_executable")
        #delay of next request after new cookies
        self.refresh_delay = self.load_config("refresh_delay")
        #delay of next execution
        self.request_delay = self.load_config("request_delay")
        #ticket price limit
        self.price_limit = Decimal(self.load_config("price_limit"))

    def load_config(self, key):
        return self.config[key] if key in self.config else None

    def get_cookie_container(self, cookie_list):
        cookie_dict = {}
        for i in range(0, len(cookie_list)):
            if cookie_list[i]['domain'] == self.domain:
                cookie_dict[cookie_list[i]['name']] = cookie_list[i]['value']
        return requests.utils.cookiejar_from_dict(cookie_dict)
    
    def get_cookie_container(self):
        if os.path.splitext(self.cookies)[1] == ".txt":
            cookie_container = http.cookiejar.MozillaCookieJar()
            cookie_container.load(self.cookies)
        else:
            cookie_container = browser_cookie3.firefox(domain_name=self.domain)

        '''
        cj = CookieJar()
        for c in cookie_container:
            if c.name == 'reese84':
                c.expires = c.expires + 3600 # 1 hour in seconds
                #86400 # 1 day in seconds
                #2592000 # 30 days in seconds
            cj.set_cookie(c)
        '''

        self.log_cookies(cookie_container)

        return cookie_container

    def wait(self, delay):
        for remaining in range(delay, 0, -1):
            sys.stdout.write("\r")
            sys.stdout.write("{:2d}s until execution continues...".format(remaining))
            sys.stdout.flush()
            time.sleep(1)
        print("\r")

    def set_default_attributes(self, data, status):
        if os.path.isfile("tracking_history.csv") == True:
            data['quantity'] = 0
            data['total'] = 0
            data['picks'] = []
            data['descriptions'] = []
            data['status'] = status
        return data
    
    def ticket_alert(self, event_id):
        #winsound.Beep(440, 5000)
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        subprocess.Popen([self.firefox_executable, "-new-tab", "https://www{domain}/event/{eventid}".format(domain = self.domain, eventid = event_id)])

    def pick_id_exists(self, tickets, id):
        return any(pick['id'] == id for pick in tickets['picks'])

    def save_pick(self, event_id, data):
        if 'picks' in data and len(data['picks']) > 0:

            #load existing picks
            directory = os.path.join("logs", "picks.json")
            if os.path.isfile(directory) == True:
                with open(directory, 'r') as file:
                    tickets = json.load(file)
            else:
                tickets = {"picks":[]}

            #add new picks
            for d in data['picks']:
                if self.pick_id_exists(tickets, d['id']) == False:

                    #alert
                    ticket_price = Decimal(d['originalPrice'])
                    price_limit = Decimal(self.price_limit)
                    if ticket_price <= price_limit:
                        self.ticket_alert(event_id)

                    #write to SQLite
                    self.insert_to_sqlite(
                        "INSERT INTO picks (EventId, Picks, CreatedOn) VALUES (?, ?, DATETIME('now','localtime'));", 
                        (event_id, json.dumps(d, cls=DateTimeEncoder))
                    )

                    #append to JSON
                    d['eventId'] = event_id
                    d['isoDate'] = datetime.datetime.now()
                    tickets['picks'].append(d)

            #save to JSON
            with open(directory, 'w', encoding='utf-8') as f:
                json.dump(tickets, f, ensure_ascii=False, indent=4, cls=DateTimeEncoder)

    def log_results(self, e, data):
        if data != None and 'status' in data:

            if 'isoDate' in data:
                del data['isoDate']
            if 'date' in data:
                del data['date']
                del data['time']

            data['eventId'] = e
            
            self.write_to_jsonl(data)
            self.write_to_csv(data)
            self.insert_to_sqlite(
                "INSERT INTO logs (EventId, Status, Quantity, Total, Picks, Descriptions, CreatedOn) VALUES (?, ?, ?, ?, ?, ?, DATETIME('now','localtime'));", 
                (data['eventId'], data['status'], data['quantity'], data['total'], json.dumps(data['picks'], cls=DateTimeEncoder), json.dumps(data['descriptions'], cls=DateTimeEncoder))
            )

    def show_trace(self, response_status, event_id, failed_events, expires):
        print(
            f"\r\n{datetime.datetime.now().strftime('%H:%M:%S')} HTTP {str(response_status).strip()}" +
            f"\r\nCurrent Event: {event_id}" +
            f"\r\nFailed Events: {len(failed_events)}" +
            f"\r\n" +
            f"\r\n".join(i for i in expires)
        )
    
    def log_cookies(self, cookie_container):
        conn = sqlite3.connect('logs\data.db') 
        cursor = conn.cursor()
        for c in cookie_container:
            expires = None
            if c.expires != None:
                expires = datetime.datetime.fromtimestamp(c.expires)
            cursor.execute("INSERT INTO cookies (Name, Value, Domain, Expires, CreatedOn) VALUES (?, ?, ?, ?, DATETIME('now','localtime'));", (c.name, c.value, c.domain, expires))
        conn.commit()
        conn.close()

    def write_to_jsonl(self, data):
        data['isoDate'] = datetime.datetime.now()
        json_directory = os.path.join("logs", "tracking_history.jsonl")
        with open(json_directory, 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, cls=DateTimeEncoder)
            f.write('\n')
        
    def write_to_csv(self, data):
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

    def insert_to_sqlite(self, insert_command, data):
        conn = sqlite3.connect('logs\data.db') 
        cursor = conn.cursor()
        cursor.execute(insert_command, data)
        conn.commit()
        conn.close()