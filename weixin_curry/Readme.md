#### 爬取微信公众号上关于库里的文章

其中自建IP代理池来自[proxy_pool](https://github.com/jhao104/proxy_pool "proxy_pool")

因为该错误信息没有保存必要,所以我用的print,如果有需要可以引用logging模块保存

requests 需要设置Cookie,请使用微信登录后的Cookie,不登录只能打开10页

爬取结果展示:
![](https://i.imgur.com/krbu4rV.png)