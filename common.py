from fastapi import FastAPI,APIRouter
from fastapi.middleware.cors import CORSMiddleware
import requests 
import json
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.firefox.service import Service

def callApi(url): 
    print('calling',url)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55"}
    try: 
        cookie_dict = json.loads(open('cookies').read())
    except Exception as error:
        cookie_dict = json.loads(open('cookies').read())
        session = requests.session()
        session.cookies.update(json.loads(open('cookies').read())) 
        for cookie in cookie_dict: 
                session.cookies.set(cookie,cookie_dict[cookie])
     
    try:
        resp = session.get(url=url, headers=headers,timeout=5)
    except Exception as error:
        cookie_dict = json.loads(open('cookies').read())
        session = requests.session()
        for cookie in cookie_dict:
            session.cookies.set(cookie,cookie_dict[cookie])
        resp = session.get(url=url, headers=headers,timeout=5)
    return resp.json() 

def get_session_cookies(): 
    service = Service()
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(service=service, options=options)
    driver.get("https://www.nseindia.com/api/equity-meta-info?symbol=APOLLOHOSP")
    cookies = driver.get_cookies()
    cookie_dict = {} 
    with open('cookies','w') as line:
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]
        line.write(json.dumps(cookie_dict)) 
    driver.quit()
    return cookie_dict