import json
import random
import smtplib
import time
from email.mime.text import MIMEText
from email.utils import formataddr

import requests

sender_addr = 'vip@takfu.tk'
receiver_addr = '402189952@qq.com'


def run(url, param, px):
    if px:
        proxies = {'http': '127.0.0.1:1081',
                   'https': '127.0.0.1:1081'
                   }
        r = requests.post(url, param, proxies=proxies)
    else:
        r = requests.post(url, param)

    r.raise_for_status()
    jstr = r.text

    air_info = json.loads(jstr)
    airList = air_info['searchProduct']
    list = []
    for air in airList:
        price = air['salePrice']
        if price and int(price) > 0:
            print('grab ok!')
            vv = {}
            vv.update({'售价': price, '限重': air['baggageAllowance'], '仓位': air['cabin']['baseCabinCode'],
                       '折扣': air['discount']})
            list.append(vv)

    print(list)
    if list:
        print('prepare send email')
        send_email(subj='机票来了', detail='需要起来抢票了TCC，地址:{%s},信息\r\n %s' % (url, str(list)))
    else:
        print('无票 安耽睡觉')


def send_email(subj='机票来了', detail='机票来了', sender_nick='水盆羊肉', receiver_nick='收件人昵称'):
    try:
        msg = MIMEText(detail, 'plain', 'utf-8')
        msg['From'] = formataddr([sender_nick, 'vip@takfu.tk'])
        msg['To'] = formataddr([receiver_nick, '402189952@qq.com'])
        msg['Subject'] = subj
        server = smtplib.SMTP_SSL("mail.takfu.tk", 465)
        server.login(sender_addr, password='230240032fth')
        server.sendmail(sender_addr, [receiver_addr, ], str(msg))
        server.quit()  # 关闭连接
        print("发送成功")
    except Exception as e:
        print("发送失败")
        raise e


if __name__ == '__main__':
    url = r'http://www.ceair.com/otabooking/flight-search!doFlightSearch.shtml'

    # 东京上海
    param = {'_': '5ed26ab082ae11e3daw3474c66149b97',
             'searchCond': '{"adtCount":1,"chdCount":0,"infCount":0,"currency":"CNY","tripType":"OW","recommend":false,"reselect":"","page":"0","sortType":"a","sortExec":"a","segmentList":[{"deptCd":"HND","arrCd":"SHA","deptDt":"2020-04-24","deptAirport":"","arrAirport":"","deptCdTxt":"东京","arrCdTxt":"上海","deptCityCode":"TYO","arrCityCode":"SHA"}],"version":"A.1.0"}'}

    # 北京上海
    # param = {'_': '5ed26ab082ae11eaab73474c66149b97',
    #          'searchCond': '{"adtCount":1,"chdCount":0,"infCount":0,"currency":"CNY","tripType":"OW","recommend":false,"reselect":"","page":"0","sortType":"a","sortExec":"a","segmentList":[{"deptCd":"SHA","arrCd":"PEK","deptDt":"2020-04-24","deptAirport":"","arrAirport":"","deptCdTxt":"上海","arrCdTxt":"北京","deptCityCode":"SHA","arrCityCode":"BJS"}],"version":"A.1.0"}'}

    mn = input(r'输入轮询区间最小秒数:  ')
    mx = input(r'输入轮询区间最大秒数:  ')
    # print(r'输入要跟踪的机票网页，例如: http://www.ceair.com/booking/hnd-sha-200424_CNY.html')
    # trackurl = input(r'输入跟踪网页，直接回车跟踪东京-上海4月24航班: ')
    #
    # if trackurl:
    #     url = trackurl

    print("轮询区间最小[/秒]: %s \r\n轮询区间最大[/秒]: %s " % (mn, mx))

    px = input(r'是否需要开启代理?输入任意字符开启代理，直接回车不需要代理:')
    confirm = input(r'回车确认开始任务')
    while True:
        try:
            run(url, param, px)
            time.sleep(random.randint(int(mn), int(mx)))
        except:
            print("some error occur ,job still running on")
            pass
