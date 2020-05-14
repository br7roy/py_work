import random
import smtplib
import time
from email.mime.text import MIMEText
from email.utils import formataddr

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sender_addr = 'vip@takfu.tk'
receiver_addr = '*********@qq.com'

cnt = 0

dd = None


def send_email(subj='机票来了', detail='机票来了', sender_nick='水盆羊肉', receiver_nick='收件人昵称'):
    try:
        msg = MIMEText(detail, 'plain', 'utf-8')
        msg['From'] = formataddr([sender_nick, 'vip@takfu.tk'])
        msg['To'] = formataddr([receiver_nick, '*******@qq.com'])
        msg['Subject'] = subj
        server = smtplib.SMTP_SSL("mail.takfu.tk", 465)
        server.login(sender_addr, password='*********')
        server.sendmail(sender_addr, [receiver_addr, ], str(msg))
        server.quit()  # 关闭连接
        print("发送成功")
    except Exception as e:
        print("发送失败")
        raise e


def run(sp, p):
    target = sp.findAll('article', attrs={'class': 'flight'})
    for elem in target:
        tar = elem.findAll("section", attrs={'class': 'detail'})
        if not tar:
            continue
        for e in tar:
            dd = e.findAll('dd')
            if not dd:
                continue
            for d in dd:
                cls = d.get_attribute_list('class')
                if not cls:
                    continue
                for c in cls:
                    if str(c).startswith('price'):
                        print('需要起来抢票了TCC')
                        send_email(subj='机票来了', detail='需要起来抢票了TCC，地址:{}'.format(p))
                        break
                    else:
                        print('票还没到，安心睡觉')
                break
            break
        break


def mock(p, driverPath):
    global cnt
    global dd

    if cnt == 0:
        try:
            dd = webdriver.Chrome()
        except:
            dd = webdriver.Chrome(executable_path=driverPath)
        cnt = cnt + 1
    else:
        dd.refresh()

    print("正在打开网页...")
    dd.get(p)
    print("等待网页响应...")
    wait = WebDriverWait(dd, 10)
    # 需要等一下，直到页面加载完成
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'summary')))
    print("等待网页响应...")

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'font-size12')))

    soup = BeautifulSoup(dd.page_source, "html5lib")
    print('540' in soup.text)
    return soup


if __name__ == '__main__':
    # path = 'http://www.ceair.com/booking/sha-kmg-200424_CNY.html'

    path = r'http://www.ceair.com/booking/hnd-sha-200424_CNY.html'
    print(
        '请输入GoogleDriver存储地址！driver下载地址为:\nhttps://sites.google.com/a/chromium.org/chromedriver/downloads \n下载完以后记录存放地址'
        '\n请核对当前chrome浏览器得版本，下载对应版本的driver!')
    driverPath = input('请输入GoogleDriver存储地址')
    print("你输入的内容是: ", driverPath)
    print(r'请输入每次模拟刷新页面得频率范围输入最小与最大2个数字，列入 1 60,系统会从1秒到60秒中随机挑选时间模拟访问网站')
    mn = input(r'输入最小秒数:  ')
    mx = input(r'输入最大秒数:  ')
    print(r'输入要跟踪的机票网页，例如: http://www.ceair.com/booking/hnd-sha-200424_CNY.html')
    trackurl = input(r'输入跟踪网页，直接回车跟踪东京-上海4月24航班: ')

    if trackurl:
        path = trackurl

        print("driver地址: %s \r\n最小: %s \r\n最大: %s \r\n跟踪地址: %s" % (driverPath, mn, mx, trackurl))

    confirm = input(r'回车确认开始任务')

    while True:
        try:
            soup = mock(path, driverPath)
            run(soup, path)
            time.sleep(random.randint(int(mn), int(mx)))
        except:
            pass

# if __name__ == '__main__':
#     send_email()
