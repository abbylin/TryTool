from bs4 import BeautifulSoup
import urllib
import json  # 使用了json格式存储
import datetime
from selenium import webdriver


def dealWithCurrentPage():
    # url = 'https://careers.tencent.com/'
    # request = urllib.request.Request(url + 'search.html?pcid=40001')
    # request = urllib.request.Request('https://try.jd.com/activity/getActivityList?page=1&activityState=0')
    # response = urllib.request.urlopen(request)
    # htmlhandle = response.read()

    # test
    htmlfile = open('test.html', 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    html = BeautifulSoup(htmlhandle, 'lxml')

    # 创建CSS选择器
    result = html.select("div[class='items']")
    if len(result) == 0:
        print("未找到产品列表")
        return

    itemList = result[0].find_all("li")
    products = []
    for item in itemList:
        product = {}

        product_name = item.select("div[class='p-name']")[0].get_text()
        product_id = item.attrs['activity_id']
        link = item.select("div[class='try-item'] a")[0].attrs['href']
        daysleft = 0
        time_stamp = item.attrs['end_time']
        if len(time_stamp) > 0:
            end_date = datetime.date.fromtimestamp(int(time_stamp)/1000)
            today = datetime.date.today()
            daysleft = end_date.__sub__(today).days

        product['name'] = product_name
        product['product_id'] = product_id
        product['link'] = link
        product['days_left'] = daysleft

        if int(daysleft) < 10:
            products.append(product)

    applyForProdcut(products[0])

    # # 禁用ascii编码，按utf-8编码
    # line = json.dumps(products, ensure_ascii=False)
    #
    # output.write(line.encode(encoding='UTF-8'))
    # output.close()

def applyForProdcut(product):
    link = product['link']
    if len(link) > 0:
        driver = webdriver.Chrome()
        driver.get(link)
        driver.quit()

3、解压下载的驱动放到指定目录，代码调用时指定该目录即可。

我把它放在了selenium下的chrome了，代码演示如下

from selenium import webdriver

chrome_driver = r"C:\Python37\Lib\site-packages\selenium\webdriver\chrome\chromedriver.exe"
browser = webdriver.Chrome(executable_path=chrome_driver)



if __name__ == "__main__":
    dealWithCurrentPage()