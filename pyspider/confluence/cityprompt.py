import requests
from bs4 import BeautifulSoup


class CityInfo(object):
    def __init__(self, city_code, city_name, down):
        self.city_code = city_code
        self.city_name = city_name
        self.down = down

    def __str__(self) -> str:
        return "code:" + self.city_code + "name:" + self.city_name + "down" + self.down

    __repr__ = __str__


cf_home_url = ""
cf_page_url = cf_home_url + ""

login_data = {
    "os_username": "",
    "os_password": "",
    "login": "登录",
    "os_destination": "",
}

loginreqsession = None


def login(user, pwd):
    login_data.update({"os_username": user})
    login_data.update({"os_password": pwd})
    # 登录
    global loginreqsession
    loginreqsession = requests.session()
    loginreqsession.post(cf_home_url, login_data).content.decode("utf-8")


def attach_page():
    global loginreqsession
    # 访问某个页面
    page_html_text = loginreqsession.get(cf_page_url).content.decode("utf-8")
    soup = BeautifulSoup(page_html_text, 'html5lib')
    # table = soup.select("table.wrapped.fixed-table.confluenceTable")
    table = soup.find('tbody')
    tr = table.findAll('tr')
    data = {}
    import re
    cp = re.compile("^.*<p>.*$|^.*</p>.*$|^.*<br/>.*$|^.*<br>.*$|^.*\xa0.*$", re.IGNORECASE)
    last_batch_no = ''
    for elem in tr:
        td = elem.find_all('td')
        tmp = []
        for city_info in td:
            line = str(city_info.contents[0])
            line = cp.sub("", line)
            tmp.append(line)
            # print(line)
        if len(tmp) == 0:
            continue
        try:
            if len(tmp) == 4:
                # 说明这是带批次column的
                # 保存批次
                batch_no = tmp[0]
                last_batch_no = batch_no
                city_code = tmp[1]
                city_name = tmp[2]
                down = tmp[3] if tmp[3] is not None else ""
                # checkDict 是否存在batch
                if batch_no not in data.keys():
                    # 不存在
                    data.setdefault(batch_no, [CityInfo(city_code, city_name, down)])
                else:
                    # 存在
                    city_arr = data[batch_no]
                    city_arr.append(CityInfo(city_code, city_name, down))
            if len(tmp) == 3:
                city_code = tmp[0]
                city_name = tmp[1]
                down = tmp[2] if tmp[2] is not None else ""
                if last_batch_no not in data.keys():
                    data.setdefault(last_batch_no, CityInfo(city_code, city_name, down))
                else:
                    city_arr = data[last_batch_no]
                    city_arr.append(CityInfo(city_code, city_name, down))
        except:
            pass

    print("===================>CITY_INFO:<===================\n\n\n")
    for k, v in data.items():
        print("k:%sv:%s" % (k, v))
    print("\n\n\n")
    print(f"any problem report to page: {cf_page_url}")


if __name__ == '__main__':
    import sys
    arg = sys.argv
    if len(arg) != 3:
        print("input account password")
        sys.exit(-1)
    login(arg[1], arg[2])
    attach_page()
