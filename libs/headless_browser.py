import json
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

class headless_browser:

    def setup_firefox(self, header_dict, url):

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
        print(driver.title)

        source = driver.page_source
        driver.quit()
        return source

    def setup_chrome(self, url):

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
        print(driver.title)

        source = self.driver.page_source
        driver.quit()
        return source
    
    def convert_source_to_json(self, source):
        soup = BeautifulSoup(source, 'html.parser')
        pre = soup.find_all('pre')[-1]
        pre_text = pre.text.strip()
        data = json.loads(pre_text)
        print(data)

        return data