#!/bin/bash/python3
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pyspider.tblogin.EmailToolKit import send_email

s = requests.Session()

tag = 'aria-disabled'


def go(cookies):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Sec-Fetch-Mode": "no-cors",
        "Referer": "https://detail.tmall.com/item.htm?id=597859359278&spm=a1z09.2.0.0.502d2e8dIVO2BH&_u=s1vdkdec936&sku_properties=1627207:28341"}
    s.headers = header
    path = 'https://detail.tmall.com/item.htm?id=597859359278&spm=a1z09.2.0.0.502d2e8dIVO2BH&_u=s1vdkdec936&skuId=4175113913314'

    # 打开chrome浏览器（需提前安装好chromedriver）
    browser = webdriver.Chrome()
    # browser = webdriver.PhantomJS()
    browser.add_cookie(cookies)

    print("正在打开网页...")
    browser.get(path)
    print("等待网页响应...")
    # 需要等一下，直到页面加载完成
    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "aria-disable")))

    soup = BeautifulSoup(browser.page_source, 'html5lib', from_encoding='iso8859-1')
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
    path = 'https://detail.tmall.com/item.htm?id=597859359278'

    # desire_cap = DesiredCapabilities.CHROME
    # desire_cap["PageLoadStrategy"] = "none"
    # opts = webdriver.ChromeOptions()
    # opts.set_capability("pageLoadStrategy", "none")
    # 打开chrome浏览器（需提前安装好chromedriver）
    # driver = webdriver.Chrome(chrome_options=opts)
    driver = webdriver.Chrome()
    print("正在打开网页...")
    driver.get(path)
    print("等待网页响应...")
    wait = WebDriverWait(driver, 10)
    # 需要等一下，直到页面加载完成
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'tm-clear J_TSaleProp')))
    print("等待网页响应...")

    # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "aria-disabled")))
    # wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tb-prop')))
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'tm-clear J_TSaleProp')))
    # b = wait.until(EC.element_to_be_clickable(
    #     (By.XPATH, "//*[@id='J_DetailMeta']/div[1]/div[1]/div/div[6]/div/div/dl[1]/dd/ul/li[11]/a"))).click()
    soup = BeautifulSoup(driver.page_source, "html5lib")
    print('aria-disabled' in soup.text)
    with open(r'c:/users/administrator/desktop/5.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
