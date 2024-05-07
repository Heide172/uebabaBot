from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent

JOKE_URL = 'https://baneks.ru/random'


def get_joke():
    req = requests.get(JOKE_URL)
    soup = BeautifulSoup(req.text, 'html.parser')
    joke = soup.find('article')
    return joke.text

if __name__ == '__main__':
    print(get_joke())