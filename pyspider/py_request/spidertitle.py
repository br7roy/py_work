import requests
import re
from bs4 import BeautifulSoup


def start():
    r = requests.get("https://testerhome.com/topics/last")
    soup = BeautifulSoup(r.text, 'html.parser')
    target = soup.select("div.title.media-heading")

    for ele in target:
        res = re.search(r'title="(.*?)"', str(ele))
        print(res.group(1))


if __name__ == '__main__':
    start()
