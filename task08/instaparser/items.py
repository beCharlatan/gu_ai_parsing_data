# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    root_user_id = scrapy.Field()
    root_user_name = scrapy.Field()
    relative_key = scrapy.Field()
    target_user_id = scrapy.Field()
    target_user_name = scrapy.Field()
    target_user_avatar_url = scrapy.Field()
