# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from qidian.spiders.rank import RankSpider


class QidianPipeline(object):

    def __init__(self):
        self.cache = []

    def process_item(self, item, spider):
        self.cache.append(dict(item))
        return item

    def close_spider(self, spider):
        if isinstance(spider, RankSpider):
            self.cache.sort(key=lambda item: int(item['rank']))

        with open(spider.name + '-' + spider.type + '.json', 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=4, ensure_ascii=False)
