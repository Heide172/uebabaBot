from bs4 import BeautifulSoup
import random
import json
import requests
import datetime
from fake_useragent import UserAgent

ua = UserAgent()
JOKE_URL = 'https://baneks.ru/random'

headers = {
    'accept': 'application/json, text/plain, */*',
    'user-Agent': ua.google,
}

def get_joke():
    req = requests.get(JOKE_URL, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    joke = soup.find('article')
    return joke.text

if __name__ == '__main__':
    print(get_joke())