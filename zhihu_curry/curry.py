import re
from random import randint
from time import sleep

import pymongo
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0'}  # 设置user-agent冒充为浏览器
feed_url = 'https://www.zhihu.com/search?type=content&q=%E5%BA%93%E9%87%8C'  # 知乎搜索库里后的初始url

client = pymongo.MongoClient(host='127.0.0.1', port=27017)  # 建立MongoDB的连接
db = client.curry  # 连接名为curry数据库  如没有该数据库会自动创建该数据库


# 获取问题页面的置顶答案
def get_anwser_content(url):
    try:
        anwser_html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(anwser_html, 'lxml')
        content_html = str(soup.find_all('div', {'class': 'QuestionAnswer-content'}))
        content = BeautifulSoup(content_html, 'lxml').get_text()
        return content
    except Exception as e:
        print(e)


# 获取专栏的文章
def get_zhuanlan_content(url):
    try:
        zhuanlan_html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(zhuanlan_html, 'lxml')
        content_html = str(soup.find_all('div', {'class': 'RichText ztext Post-RichText'}))
        content = BeautifulSoup(content_html, 'lxml').get_text()
        return content
    except Exception as e:
        print(e)


def main():
    # 要将火狐浏览器内核驱动配置到你的环境变量,该方法会自行启动浏览器 不管用什么浏览器都需要先配置内核
    driver = webdriver.Firefox()
    driver.get(feed_url)  # 在浏览器中输入的网址
    js = 'window.scrollTo(0,document.body.scrollHeight)'  # 让滚动条滚动至浏览器最底部
    for _ in range(20):  # 知乎的页面是动态加载的,循环将滚动条滚动至最底部20次,实际可能没这么多次
        driver.execute_script(js)  # 执行JavaScript语句
        sleep(randint(3, 4))  # 动态加载页面需要等待时间,(根据网速设置等待时间),也可以避免被识别为异常请求
    soup = BeautifulSoup(driver.page_source, 'lxml')  # 取出加载完成后的全部页面
    title_list = soup.find_all('span', {'class': 'Highlight'})  # 取出全部问题或专栏标题
    id_num = 0  # 设置ID,方便管理MongoDB
    for q_tag in title_list:
        title = q_tag.get_text()  # 拿到问题或专栏标题的字符内容
        try:
            a_tag = str(q_tag.parent)
            soup = BeautifulSoup(a_tag, 'lxml')
            url = soup.a['href']
            if re.match('/question/\d+/answer/\d+', url):  # 拿到问题的相对http地址
                url = 'https://www.zhihu.com' + url  # 拿到绝对地址
                content = get_anwser_content(url)  # 获取问题的置顶答案文章
            else:
                url = 'https:' + url  # 拿到专栏的http绝对地址
                content = get_zhuanlan_content(url)  # 获取专栏文章

            id_num += 1
            db.zhihu.insert_one(
                {'_id': id_num, 'title': title, 'url': url, 'content': content})  # 保存到MongoDB的curry->zhihu中
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
