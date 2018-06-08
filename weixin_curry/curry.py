import pymongo
import requests
from urllib.parse import urlencode
from lxml.etree import XMLSyntaxError
from pyquery import PyQuery as pq
from requests.exceptions import ConnectionError

PROXY_POOL_URL = 'http://127.0.0.1:5010/get'  # 自建的PROXY代理池
KEYWORD = '库里'  # 你想要查询文章的关键字
MAX_TIMES = 5  # 最大连接次数
client = pymongo.MongoClient(host='127.0.0.1', port=27017)  # 连接Mongo
db = client.weixin

base_url = 'http://weixin.sogou.com/weixin?'

headers = {
    'Cookie': '',  # 在浏览器登录后复制你的cookie 不登录只能访问10页
    'Host': 'weixin.sogou.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0'
}

proxy = None


# 如果反爬禁止了IP则从代理池取出一个代理IP
def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError as e:
        print(e)


def get_html(url, try_times=1):
    print('正在爬取', url)
    print('尝试第%d次' % try_times)
    global proxy
    if try_times >= MAX_TIMES:
        print('获取%s失败' % url)
        return None
    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy
            }
            response = requests.get(url, allow_redirects=False, headers=headers, proxies=proxies)
        else:
            response = requests.get(url, allow_redirects=False, headers=headers)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            print('302')
            proxy = get_proxy()
            if proxy:
                print('使用代理IP:', proxy)
                return get_html(url)
            else:
                print('获取代理IP失败')
                return None
    except ConnectionError as e:
        print('error:', e.args)
        proxy = get_proxy()
        try_times += 1
        return get_html(url, try_times)


def get_index(keyword, page):
    data = {
        'query': keyword,
        'type': 2,
        'page': page
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html


def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('href')


def get_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError as e:
        print(e)


def parse_detail(html):
    try:
        doc = pq(html)
        title = doc('#activity-name').text()
        writer = doc('#profileBt > a:nth-child(1)').text()
        content = doc('.rich_media_content').text()
        return {
            'title': title,
            'writer': writer,
            'content': content,
        }
    except XMLSyntaxError as e:
        print(e)


def save_data(data):
    if db['articles'].update({'title': data['title']}, {'$set': data}, True):
        print('保存成功')
    else:
        print('保存失败')


def main():
    for page in range(1, 101):           # 爬取100页
        html = get_index(KEYWORD, page)
        if html:
            article_urls = parse_index(html)
            for article_url in article_urls:
                article_html = get_detail(article_url)
                if article_html:
                    article_data = parse_detail(article_html)
                    print(article_data)
                    if article_data:
                        save_data(article_data)


if __name__ == '__main__':
    main()
