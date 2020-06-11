from bs4 import BeautifulSoup
import urllib
import json  # 使用了json格式存储
import time
import datetime


def productsCatching():
    # url = 'https://careers.tencent.com/'
    # request = urllib.request.Request(url + 'search.html?pcid=40001')
    # request = urllib.request.Request('https://try.jd.com/activity/getActivityList?page=1&activityState=0')
    # response = urllib.request.urlopen(request)
    # htmlhandle = response.read()

    output = open('tencent.json', 'wb+')

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

        name = item.select("div[class='p-name']")[0].get_text()
        id = item.attrs['activity_id']
        link = item.select("div[class='try-item'] a")[0].attrs['href']
        daysleft = 0
        time_stamp = item.attrs['end_time']
        if len(time_stamp) > 0:
            end_date = datetime.date.fromtimestamp(int(time_stamp)/1000)
            today = datetime.date.today()
            daysleft = end_date.__sub__(today).days

        product['name'] = name
        product['id'] = id
        product['link'] = link
        product['days_left'] = daysleft

        products.append(product)

    # 禁用ascii编码，按utf-8编码
    line = json.dumps(products, ensure_ascii=False)

    output.write(line.encode(encoding='UTF-8'))
    output.close()


if __name__ == "__main__":
    productsCatching()