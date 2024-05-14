from bs4 import BeautifulSoup
import requests

JOKE_URL = 'https://baneks.ru/random'
MEME_URL = ''


def get_joke():
    req = requests.get(JOKE_URL)
    soup = BeautifulSoup(req.text, 'html.parser')
    joke = soup.find('article')
    return joke.text
def get_meme():
    req = requests.get()
if __name__ == '__main__':
    print(get_joke())