# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline


class SaveImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        return request.url.split('/')[-1]

    def get_media_requests(self, item, info):
        yield Request(url=item['img_url'])

    def item_completed(self, results, item, info):
        if not results[0][0]:
            raise DropItem('下载失败')
        return item


class SaveToMongoPipeline(object):
    collection_name = 'img'

    def __init__(self, mongo_client, mongo_db):
        self.mongo_client = mongo_client
        self.mongo_db = mongo_db

    def open_spider(self,spider):
        self.client = MongoClient(self.mongo_client)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('MONGO_CLIENT'),
                   crawler.settings.get('MONGO_DB','items'))