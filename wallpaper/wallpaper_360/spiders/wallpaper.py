# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode

import scrapy

from wallpaper_360.items import Wallpaper360Item


class WallpaperSpider(scrapy.Spider):
    name = 'wallpaper'
    allowed_domains = ['image.so.com']

    def start_requests(self):
        base_url = 'http://image.so.com/zj?'
        param = {
            'ch': 'wallpaper',
            't1': 157,
            'width': 1920,
            'height': 1200,
            'listtype': 'new',
            'temp': 1
        }
        for page in range(10):
            param['sn'] = page * 30
            full_url = base_url + urlencode(param)
            yield scrapy.Request(url=full_url, callback=self.parse)

    def parse(self, response):
        model_dict = json.loads(response.text)
        for elem in model_dict['list']:
            item = Wallpaper360Item()
            item['title'] = elem['group_title']
            item['tag'] = elem['tag']
            item['img_url'] = elem['qhimg_url']
            yield item
