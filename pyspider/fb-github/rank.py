import requests
from bs4 import BeautifulSoup
import re


def start(page):
    cache = {}
    mark = 'stargazers'
    i = 1
    while True:
        try:
            r = requests.get(page + str(i))
            r.raise_for_status()
            i += 1
            soup = BeautifulSoup(r.text, 'html5lib')
            target = soup.select("a.no-wrap.muted-link.mr-3")

            for elem in target:
                txt = str(elem)
                group = re.search(r'href="(.*?)"', txt)
                res = group.group(1)[1:]
                s_index = res.rindex("/") + 1
                if res[s_index:] != mark:
                    continue
                first_s_idx = res.index("/") + 1
                p_name = res[first_s_idx:res.rindex("/")]
                s = txt.index('</svg>')
                e = txt.rindex('</a>')
                star = txt[s + 7:e]
                p_star = re.sub('(\\s+)', '', star)
                p_star = re.sub(',', '', p_star)
                cache.update({p_name: int(p_star)})
        except:
            break
    return cache


if __name__ == '__main__':
    s_page = r'https://github.com/facebook?page='
    cache = start(s_page)
    print('total project ', len(cache))
    cache = sorted(cache.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    top10 = cache[:10]
    for ele in top10:
        print(ele)
