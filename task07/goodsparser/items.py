# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst

def process_price(value: str) -> str:
    try:
        value = value.replace(' ', '')
        value = int(value)
    except Exception as e:
        print(e)
    finally:
        return value


class GoodsparserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    cost = scrapy.Field(input_processor=MapCompose(process_price), output_processor=TakeFirst())
    image_urls = scrapy.Field()
    images = scrapy.Field()
