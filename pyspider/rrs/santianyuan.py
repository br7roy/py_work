import os
import smtplib
import time
from email.mime.text import MIMEText
from email.utils import formataddr

import feedparser
import requests

flg = 0


def send_email(subj='家政夫三田园更新了', detail='家政夫三田园更新了', sender_nick='发件人昵称', receiver_nick='收件人昵称'):
    try:
        msg = MIMEText(detail, 'plain', 'utf-8')
        msg['From'] = formataddr([sender_nick, 'no-reply'])
        msg['To'] = formataddr([receiver_nick, 'no-reply'])
        msg['Subject'] = subj
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login('82763623@qq.com', 'qrlkjqswnqvsbiae')
        server.sendmail('82763623@qq.com', ['82763623@qq.com', ], str(msg))
        server.quit()  # 关闭连接
        print("发送成功")
    except Exception as e:
        print("发送失败")
        raise e


def run(url):
    r = requests.get(url)
    r.raise_for_status()
    feed = feedparser.parse(r.text)
    if len(feed.entries) > 2:
        send_email()
        global flg
        flg = 2
    else:
        print("no update")


if __name__ == '__main__':
    url = r'http://rss.rrys.tv/rss/feed/39886'
    while 1 and flg == 0:
        run(url)
        time.sleep(1 * 60)
