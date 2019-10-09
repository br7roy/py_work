import time

import requests
import json
import os
import re

from pyspider.tblogin.EmailToolKit import send_email
requests.adapters.DEFAULT_RETRIES = 15
s = requests.Session()
s.keep_alive = False
# above refer https://www.cnblogs.com/tig666666/p/9296466.html

COOKIE_FILE_PATH = os.path.abspath('cookie.txt')


class UserNameLogin:
    def __init__(self, userName, ua, TPL_password2) -> None:
        """
        账号登录
        :param userName: 用户名
        :param ua: 淘宝ua参数
        :param TPL_password2: 加密后的密码
        """
        self.verify_password_url = 'https://login.taobao.com/member/login.jhtml'
        self.nick_check_url = 'https://login.taobao.com/member/request_nick_check.do?_input_charset=utf-8'
        self.login_url = "http://login.taobao.com/member/login.jhtml"
        self.vst_url = "https://login.taobao.com/member/vst.htm?st={}"
        self.adidas_good_url1 = 'https://detail.tmall.com/item.htm?id=597859359278&spm=2014.21600715.0.0'
        self.adidas_good_url2 = 'https://detail.tmall.com/item.htm?id=575795232352'
        self.userName = userName
        self.ua = ua
        self.TPL_password2 = TPL_password2
        self.timeout = 3

    def nick_check(self):
        """
        检测账号是否需要验证码
        :return:
        """
        data = {
            'username': self.userName,
            'ua': self.ua
        }
        try:
            resp = s.post(self.nick_check_url, data=data, timeout=self.timeout)
        except Exception as e:
            print('检测是否需要验证码请求失败，原因:{}', format(e))
            return True
        needcode = resp.json()['needcode']
        print('是否需要滑块验证：%s' % ('是' if needcode else '否'))
        return needcode

    def verify_password(self):
        verify_password_headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://login.taobao.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
            'Referer': 'https://login.taobao.com/member/login.jhtml?from=taobaoindex&f=top&style=&sub=true&redirect_url=https%3A%2F%2Fi.taobao.com%2Fmy_taobao.htm%3Fspm%3Da21bo.2017.754894437.3.5af911d9tZ2IjM%26ad_id%3D%26am_id%3D%26cm_id%3D%26pm_id%3D1501036000a02c5c3739',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        verify_password_data = {
            'TPL_username': self.userName,
            'ncoToken': '6ace0fa57503c63dc24106ec02952464bbe27462',
            'slideCodeShow': 'false',
            'useMobile': 'false',
            'lang': 'zh_CN',
            'loginsite': '0',
            'newlogin': '0',
            'TPL_redirect_url': 'https://detail.tmall.com/item.htm?id=597859359278&spm=a1z09.2.0.0.42692e8d5LzujT&_u=11vdkde6c54',
            'from': 'tb',
            'fc': 'default',
            'style': 'default',
            'keyLogin': 'false',
            'qrLogin': 'true',
            'newMini': 'false',
            'newMini2': 'false',
            'loginType': '3',
            'gvfdcname': '10',
            'gvfdcre': '68747470733A2F2F7777772E74616F62616F2E636F6D2F',
            'TPL_password_2': self.TPL_password2,
            'loginASR': '1',
            'loginASRSuc': '1',
            'oslanguage': 'zh-CN',
            'sr': '1440*2560',
            'naviVer': 'firefox|69',
            'osACN': 'Mozilla',
            'osAV': '5.0 (Windows)',
            'osPF': 'Win32',
            'appkey': '00000000',
            'mobileLoginLink': 'https://login.taobao.com/member/login.jhtml?from=taobaoindex&f=top&style=&sub=true&redirect_url=https://i.taobao.com/my_taobao.htm?spm=a21bo.2017.754894437.3.5af911d9tZ2IjM&ad_id=&am_id=&cm_id=&pm_id=1501036000a02c5c3739&useMobile=true',
            'showAssistantLink': '',
            'um_token': 'T0055F1DAEDFD0FA4AFF951524FD7EAA87F90EC8B26E1BAEE21FBD6E6C9',
            'ua': self.ua
        }
        try:
            resp = s.post(self.verify_password_url, headers=verify_password_headers, data=verify_password_data)
            st_token_url = re.search(r'<script src="(.*?)"></script>', resp.text).group(1)
        except Exception as e:
            print('验证用户名密码失败，原因:{}'.format(e))
            return None
        if st_token_url:
            print('验证用户名密码成功，st码申请地址：{}'.format(st_token_url))
            return st_token_url
        else:
            print('验证用户名密码失败，请更换data参数')
            return None

    def apply_st(self):
        """
        申请st码
        :return:
        """
        apply_st_url = self.verify_password()
        try:
            st_resp = s.get(apply_st_url)
        except Exception as e:
            print('申请st码失败，原因:')
            raise e
        st_match = re.search(r'"data":{"st":"(.*?)"}', st_resp.text)
        if st_match:
            print('获取st码成功，st码:{}'.format(st_match.group(1)))
            return st_match.group(1)
        else:
            raise RuntimeError('获取st码失败')

    def get_taobao_nick_name(self):
        """
        获取淘宝昵称
        :return:
        """
        taobao_url = self.login(skip=True)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'
        }
        try:
            response = s.get(taobao_url, headers=headers)
            response.raise_for_status()
        except  Exception as e:
            print('获取淘宝主页请求失败！原因:')
            raise e
        nick_name_match = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)
        if nick_name_match:
            print('nickname : {}'.format(nick_name_match.group(1)[:3] + '***'))
            return nick_name_match.group(1)
        else:
            raise RuntimeError("获取淘宝昵称失败 response {}".format(response.text))

    def ser_cookie(self):
        """
        序列化cookie
        :return:
        """
        cookie_dict = requests.utils.dict_from_cookiejar(s.cookies)
        with open(COOKIE_FILE_PATH, 'w+', encoding='utf-8') as f:
            json.dump(cookie_dict, f)

    def deSer_cookie(self):
        """
        反序列化cookie
        :return:
        """
        with open(COOKIE_FILE_PATH, 'r+', encoding='utf-8') as f:
            cookie_dict = json.load(f)
            cookie = requests.utils.cookiejar_from_dict(cookie_dict)
            return cookie

    def load_cookie(self):
        if not os.path.exists(COOKIE_FILE_PATH):
            return False
        s.cookies = self.deSer_cookie()
        try:
            self.get_taobao_nick_name()
        except Exception as e:
            os.remove(COOKIE_FILE_PATH)
            print('cookie 过期，删除cookie文件')
            return False
        print('加载淘宝登录cookie成功')
        return True

    def login(self, skip=False):
        """
        使用st码登录淘宝
        :return:
        """
        if not skip:
            if self.load_cookie():
                return True
        # 判断滑块验证
        self.nick_check()
        st = self.apply_st()
        headers = {
            'Host': 'login.taobao.com',
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        }
        try:
            response = s.get(self.vst_url.format(st), headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('st码登录失败 原因 :')
            raise e
        taobao_match = re.search(r'top.location.href = "(.*?)"', response.text)
        if taobao_match:
            print('登录淘宝成功，跳转链接:{}'.format(taobao_match.group(1)))
            # cookies = s.cookies
            # LoopBySelenium.go(requests.utils.dict_from_cookiejar(cookies))
            # 登录成功保存cookie
            self.ser_cookie()
            return taobao_match.group(1)
        else:
            raise RuntimeError('使用st登录淘宝失败, {}'.format(response.text))

    def search_kw(self):

        urls = [self.adidas_good_url1, self.adidas_good_url2]
        for url in urls:
            r = None
            try:
                r = s.get(url)
                r.raise_for_status()
            except:
                self.login()
                r = s.get(url)
                r.raise_for_status()

            goods = re.search(r'TShop.Setup\(\s+(.*?)\s+\)', r.text)
            goods_dict = goods.group(1)
            # 4175113913309
            goods_dict = json.loads(goods_dict)
            goods_arr = goods_dict['valItemInfo']['skuList']
            skuId = ''
            for am in goods_arr:
                if re.sub(r'\s+', '', am['names']) == '42.5黑色':
                    skuId = am['skuId']
                    break
            if not skuId:
                print('skuId can not be found, check webUI!!')
                return

            mm = goods_dict['valItemInfo']['skuMap']
            for k in mm:
                gv = mm[k]
                if gv['skuId'] == skuId:
                    s_num = gv['stock']
                    if s_num > 0:
                        print('42.5库存大于0')
                        send_email(subj='42.5有货可以下单', detail='42.5有货可以下单，地址:{}'.format(url))
                    else:
                        print('42.5库存不足,url {}'.format(url))
                        # send_email(subj='42.5库存不足', detail='42.5库存不足')
                    r.close()
                    del r
                    time.sleep(5)
                    break


if __name__ == '__main__':
    ctx = ''
    with open(os.path.abspath('ua.key'), 'r+') as f:
        ctx = f.read()
    sp = ctx.split(",")
    user = UserNameLogin(sp[0].replace("'", ""), sp[1].replace("'", ""), sp[2].replace("'", ""))
    user.login()
    while 1:
        user.search_kw()
        time.sleep(1 * 60)
