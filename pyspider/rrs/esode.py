import os
import smtplib
import time
from email.mime.text import MIMEText
from email.utils import formataddr

import feedparser
import requests

ctx = ''
with open(os.path.abspath('email.key'), 'r+', encoding='utf-8') as f:
    ctx = f.read()
sp = ctx.split(',')

sender_addr = sp[0].replace("'", "")
receiver_addr = sp[1].replace("'", "")
token = sp[2].replace("'", "")


def send_email(subj='东京大饭店更新了', detail='东京大饭店更新了', sender_nick='发件人昵称', receiver_nick='收件人昵称'):
    try:
        msg = MIMEText(detail, 'plain', 'utf-8')
        msg['From'] = formataddr([sender_nick, sender_addr])
        msg['To'] = formataddr([receiver_nick, receiver_addr])
        msg['Subject'] = subj
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(sender_addr, token)
        server.sendmail(sender_addr, [receiver_addr, ], str(msg))
        server.quit()  # 关闭连接
        print("发送成功")
    except Exception as e:
        print("发送失败")
        raise e


def run(url):
    r = requests.get(url)
    r.raise_for_status()
    feed = feedparser.parse(r.text)
    if len(feed.entries) > 5:
        send_email()
    else:
        print("no update")


if __name__ == '__main__':
    url = r'http://rss.rrys.tv/rss/feed/38941'
    while 1:
        run(url)
        time.sleep(1 * 60)
