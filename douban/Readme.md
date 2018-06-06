#### 爬取豆瓣电影Top250的电影

**爬取的内容为电影名称 分数 一句话描述**

利用scrapy框架进行爬虫,
豆瓣进行了反爬设置,所以我设置了IP代理池与用户代理

代理IP来自[proxy_pool](https://github.com/jhao104/proxy_pool "proxy_pool")

利用此列示范如何在scrpy中设置IP以及用户代理,连接使用MongoDB数据库

以及scrapy框架的简单使用

爬取结果展示
![](https://i.imgur.com/BUXotRj.png)