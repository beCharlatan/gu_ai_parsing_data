# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from pymongo import MongoClient
import scrapy
from scrapy.pipelines.images import ImagesPipeline

class GoodsparserPipeline:
    collection_name = "lm_goods"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()


    def process_item(self, item, spider):
        mongo_obj = {
            "url": item['url'],
            "title": item['title'],
            "cost": item['cost'],
            "images_data": item['images'],
        }
        self.db[self.collection_name].insert_one(mongo_obj)
        return item


class GoodsImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if (item['image_urls']):
            for image_url in item['image_urls']:
                try:
                    yield scrapy.Request(image_url)
                except Exception as e:
                    print(e)

    
    def item_completed(self, results, item, info):
        item['images'] = [i[1] for i in results if i[0]]
        return item

    
    def file_path(self, request, response=None, info=None, *, item=None):
        # используем нативное имя файла (image_guid.jpg)
        original_path = super().file_path(request, response=response, info=info, item=item)
        _, filename = original_path.split('/')
        # в качестве директории используем уникальный человекочитаемый id товара
        _dir = item['url'].split('/')[-2]
        return f'{_dir}/{filename}'

