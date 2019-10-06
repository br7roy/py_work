from bs4 import BeautifulSoup

from pyspider.py_request.EmailToolKit import send_email

tag = 'aria-disabled'


class FetchAdidas:

    def __init__(self, session) -> None:
        self.s = session
        self.go()

    # 轮询阿迪王42.5码鞋子，一旦有货发邮件通知
    def go(self):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
            "Sec-Fetch-Mode": "no-cors",
            "Referer": "https://detail.tmall.com/item.htm?id=597859359278&spm=a1z09.2.0.0.502d2e8dIVO2BH&_u=s1vdkdec936&sku_properties=1627207:28341"}
        self.s.headers = header
        r = self.s.get(
            'https://detail.tmall.com/item.htm?id=597859359278&spm=a1z09.2.0.0.502d2e8dIVO2BH&_u=s1vdkdec936&skuId=4175113913314')
        r.raise_for_status()
        # r.encoding = r.apparent_encoding
        # soup = BeautifulSoup(r.text, 'html5lib')
        soup = BeautifulSoup(r.text, 'html5lib', from_encoding='iso8859-1')

        for span in soup.findAll('span'):
            if len(span.contents) > 0:
                if span.contents[0] == "42.5":
                    # 如果上架可能这个属性就没了，而不是设置为false
                    # 当然如果是false了也要发邮件
                    if tag not in span.parent.attrs:
                        # 这个也能获取属性值，明显太长，弃
                        # v = span.find_parents('a')[0].attrs['aria-disabled']
                        send_email()
                    else:
                        res = span.parent.attrs[tag]
                        if res != 'true':
                            send_email()
                    break


if __name__ == '__main__':
    go()
