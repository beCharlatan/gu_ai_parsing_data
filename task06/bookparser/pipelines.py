# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from pymongo import MongoClient

class BookparserPipeline:
    collection_name = "labirint_books"

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
        default_cost, current_cost = self.process_cost(item['cost'])
        mongo_obj = {
            "url": item['url'],
            "title": item['title'],
            "authors": item['authors'],
            "rating": self.process_rating(item['rating']),
            "default_cost": default_cost,
            "current_cost": current_cost
        }
        self.db[self.collection_name].insert_one(mongo_obj)
        return item


    def process_cost(self, cost):
        default_cost = int(cost[0])
        current_cost = None

        try:
            current_cost = int(cost[1])
        except ValueError:
            current_cost = default_cost
        finally:
            return default_cost, current_cost


    def process_rating(self, rating):
        try:
            return float(rating)
        except:
            return None