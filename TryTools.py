from bs4 import BeautifulSoup
import urllib
import json  # 使用了json格式存储
import datetime
import time
from selenium import webdriver
import re
import os.path

browser = webdriver.Chrome()
accountsDic = [{'user': 'linzhu0831@163.com', 'password': 'LINzhu2565651'}, {'user': '815924867@qq.com', 'password': 'LINzhu2565651'}]
mainURL = "https://www.jd.com"

def dealWithTrySites():
    if not os.path.isfile("channel.json"):
        return

    with open("channel.json", "rb") as fs:
        channels = fs.read()
    channels_dict = json.loads(channels)
    for channel_info in channels_dict:
        print(channel_info)
        if channel_info['channel_name'] == '生鲜美食':
            dealWithChannel(channel_info['channel_link'])

def dealWithChannel(channel_link):
    request = urllib.request.Request(channel_link)
    response = urllib.request.urlopen(request)
    htmlhandle = response.read()

    # # test
    # htmlfile = open('test.html', 'r', encoding='utf-8')
    # htmlhandle = htmlfile.read()
    html = BeautifulSoup(htmlhandle, 'lxml')

    # 创建CSS选择器
    result = html.select("div[class='items']")
    if len(result) == 0:
        print("未找到产品列表")
        return

    itemList = result[0].find_all("li")
    for item in itemList:
        product = {}

        product_name = item.select("div[class='p-name']")[0].get_text()
        product_id = item.attrs['activity_id']
        link = item.select("div[class='try-item'] a")[0].attrs['href']
        if None == re.search('https:', link):
            link = 'https:' + link

        #只申请距离结束时间小于3天的产品
        daysleft = 0
        time_stamp = item.attrs['end_time']
        if len(time_stamp) > 0:
            end_date = datetime.date.fromtimestamp(int(time_stamp)/1000)
            today = datetime.date.today()
            daysleft = end_date.__sub__(today).days

        if daysleft < 3:
            product['name'] = product_name
            product['product_id'] = product_id
            product['link'] = link
            product['days_left'] = daysleft
            applyForProdcut(product)
        else:
            print("离申请结束超过3天，不申请： " + product['name'])

def applyForProdcut(product):
    print("复合条件，申请产品： " + product['name'])
    link = product['link']
    if len(link) > 0:
        browser.get(link)
        time.sleep(2)



def loginJD(user_dict):

    if True == login_with_cookies(user_dict):
        return

    browser.get(mainURL)
    browser.maximize_window()

    #定位登录button
    browser.find_element_by_class_name("link-login").click()
    time.sleep(2)
    #定位账户登录
    browser.find_element_by_xpath('//a[text()="账户登录"]').click()
    time.sleep(2)
    #账号框，输入账号
    browser.find_element_by_xpath('//input[@name="loginname"]').send_keys(user_dict['user'])
    #密码框，输入密码
    browser.find_element_by_xpath('//input[@name="nloginpwd"]').send_keys(user_dict['password'])
    #点击登录button
    browser.find_element_by_xpath('//a[@id="loginsubmit"]').click()
    time.sleep(5)

    #获取cookie
    my_cookie = browser.get_cookies()
    data_cookie = json.dumps(my_cookie, ensure_ascii=False)
    filename = "jd_cookie_" + user_dict['user'] + ".json"
    with open(filename, "wb") as fp:
        fp.write(data_cookie.encode(encoding='UTF-8'))


def login_with_cookies(user_dict):
    filename = "jd_cookie_" + user_dict['user'] + ".json"
    if not os.path.isfile(filename):
        return False

    #清除cookies
    browser.get(mainURL)
    browser.delete_all_cookies()

    #读取本地cookies
    with open(filename, "rb") as fp:
        jd_cookies = fp.read()

    #加载cookies
    jd_cookies_dict = json.loads(jd_cookies)
    for cookie in jd_cookies_dict:
        browser.add_cookie(cookie)

    browser.refresh()
    time.sleep(2)
    #验证是否成功
    if browser.find_element_by_class_name("nickname"):
        return True
    else:
        return False



if __name__ == "__main__":
    dealWithTrySites()
    # for account in accountsDic:
    #     loginJD(account)
    #     print("用户：" + account['user'] + " 已登录，跳转试用列表")
    #     dealWithCurrentPage()