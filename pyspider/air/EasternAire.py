import time
import requests
import json
import os
import re
from bs4 import BeautifulSoup
from pyspider.tblogin.EmailToolKit import send_email
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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
                        send_email(subj='需要起来抢票了TCC', detail='需要起来抢票了TCC，地址:{}'.format(p))
                    else:
                        print('票还没到，安心睡觉')


def mock(p):
    driver = webdriver.Chrome()
    print("正在打开网页...")
    driver.get(p)
    print("等待网页响应...")
    wait = WebDriverWait(driver, 10)
    # 需要等一下，直到页面加载完成
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'summary')))
    print("等待网页响应...")

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'font-size12')))

    soup = BeautifulSoup(driver.page_source, "html5lib")
    print('540' in soup.text)
    return soup


if __name__ == '__main__':
    path = 'http://www.ceair.com/booking/sha-kmg-200424_CNY.html'
    # path = r'http://www.ceair.com/booking/hnd-sha-200424_CNY.html'

    while True:
        soup = mock(path)
        run(soup, path)
