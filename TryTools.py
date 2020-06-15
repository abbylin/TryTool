from bs4 import BeautifulSoup
import urllib.request
import json  # 使用了json格式存储
import datetime
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import os.path
import sys

browser = webdriver.Chrome()
accountsDic = [{'user': 'linzhu0831@163.com', 'password': 'LINzhu2565651'}, {'user': '815924867@qq.com', 'password': 'LINzhu2565651'}]
mainURL = "https://www.jd.com"
followedURL = "https://t.jd.com/vender/followVenderList.action?index=9"

def dealWithTrySites():
    if not os.path.isfile("channel.json"):
        return

    with open("channel.json", "rb") as fs:
        channels = fs.read()
    channels_dict = json.loads(channels)
    for channel_info in channels_dict:
        print(channel_info)
        if channel_info['channel_name'] == '生鲜美食' or channel_info['channel_name'] == '食品饮料':
            dealWithChannel(channel_info)

def dealWithChannel(channel_info):
    browser.get(channel_info['channel_link'])

    while True:

        goods_list = browser.find_element_by_id('goods-list')
        items = goods_list.find_elements_by_xpath('//li[@class="item"]')
        for item in items:
            #时间处理
            time_stamp = item.get_attribute('end_time')
            end_date = datetime.date.fromtimestamp(int(time_stamp) / 1000)
            today = datetime.date.today()
            daysleft = end_date.__sub__(today).days

            #产品名称黑白列表处理
            name = item.find_element_by_class_name('p-name').text
            name_verified = True
            if 'channel_blacklist' in channel_info:
                blacklist_re = '|'.join(channel_info['channel_blacklist'])
                name_verified = not bool(re.search(blacklist_re, name) != None)

            if 'channel_whitelist' in channel_info:
                whitelist_re = '|'.join(channel_info['channel_whitelist'])
                name_verified = bool(re.search(whitelist_re, name) != None)

            #只申请距离结束3天之内的产品，产品名称不能在黑名单之内
            if name_verified and daysleft < 3:
                #打开试用产品申请页
                link = item.find_element_by_class_name('link').get_attribute('href')
                if None == re.search('https:', link):
                    link = 'https:' + link
                js = 'window.open(' + '\"' + link +'\"' + ')'
                browser.execute_script(js)
                handles = browser.window_handles
                browser.switch_to.window(handles[1])

                while True:
                    # 循环尝试申请直到成功为止
                    # 点击申请
                    apply_btn = WebDriverWait(browser, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//a[text()="申请试用"]')))
                    apply_btn.click()

                    # 检查是否弹出"关注并申请"对话框
                    try:
                        follow_apply_btn = WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.XPATH,
                                                                                                           '//div[@class="ui-dialog"]/div[@class="ui-dialog-content"]/div/div/div[@class="btn"]/a[text()="关注并申请"]')))
                        follow_apply_btn.click()
                    except:
                        None

                    time.sleep(2)
                    try:
                        alert_tip = browser.find_element_by_xpath('//div[@class="ui-dialog tipsAlert"]/div[@class="ui-dialog-content"]/div/div[1]').text
                    except:
                        alert_tip = ""

                    if re.search('未关注店铺', alert_tip):
                        # 未关注店铺，申请失败，先进店关注
                        browser.refresh()
                        time.sleep(2)
                        if browser.find_element_by_xpath(
                                '//a[@class="btn-def follow-shop J-follow-shop"]').text == "关注店铺":
                            mall_link = browser.find_element_by_xpath(
                                '//a[@class="btn-def enter-shop J-enter-shop"]').get_attribute('href')
                            browser.get(mall_link)
                            follow_btn = WebDriverWait(browser, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@id="shop-attention"]')))
                            follow_btn.click()
                            time.sleep(1)
                            #后退并刷新，等待尝试再次申请
                            browser.back()
                            browser.refresh()
                            time.sleep(2)
                    elif re.search('申请成功|京享值', alert_tip):
                        #申请成功，退出循环
                        break
                    elif re.search('超过上限', alert_tip):
                        #申请数达到上限，抛出异常
                        raise ValueError('申请数量超过上限')
                    elif re.search('关注上限', alert_tip):
                        clean_followed_malls()
                        browser.refresh()
                        time.sleep(2)
                    else:
                        break

                # follow_apply_btn = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '//a[text()="关注并申请"]')))
                # is_visible = bool(EC.visibility_of_element_located((By.XPATH,'//a[text()="关注并申请"]'))(browser))

                #申请成功，关闭当前页，回到试用列表
                browser.close()
                browser.switch_to.window(handles[0])

                # 等待5秒再进行下一个申请
                time.sleep(5)

        # 下一页
        try:
            next_page_button = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//a[@class="ui-pager-next"]')))
            next_page_button.click()
            time.sleep(2)
        except:
            #已经到了最后一页，退出循环
            break

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


def clean_followed_malls():
    js = 'window.open(' + '\"' + followedURL + '\"' + ')'
    browser.execute_script(js)
    handles = browser.window_handles
    tab_index = len(handles)
    browser.switch_to.window(handles[tab_index-1])
    browser.find_element_by_xpath('//div[@class="batch-box J-batchBox"]/a[@class="btn-def batch-btn"]').click()
    browser.find_element_by_xpath('//div[@class="batch-operate"]/span[@class="op-btn u-check"]').click()
    browser.find_element_by_xpath('//div[@class="batch-operate"]/span[@class="op-btn u-unfollow"]').click()
    browser.close()
    browser.switch_to.window(tab_index - 2)

if __name__ == "__main__":
    for account in accountsDic:
        # if account['user'] == '815924867@qq.com':
        #     continue
        try:
            loginJD(account)
            print("用户：" + account['user'] + " 已登录，跳转试用列表")
            dealWithTrySites()
        except ValueError as err:
            continue