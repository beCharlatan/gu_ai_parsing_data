import scrapy
from scrapy.http import HtmlResponse
from items import GoodsparserItem
from scrapy.loader import ItemLoader

class LmspiderSpider(scrapy.Spider):
    name = 'lmspider'
    allowed_domains = ['leroymerlin.ru']
    start_urls = [
        'https://leroymerlin.ru/catalogue/dreli-shurupoverty/'
    ]

    def parse(self, response):
        next_url = response.xpath('//a[@data-qa-pagination-item="right"]/@href').get()
        if next_url:
            yield response.follow(next_url, callback=self.parse)

        goods_links = response.xpath('//a[@data-qa="product-image"]/@href').getall()
        for good_link in goods_links:
            yield response.follow(good_link, callback=self.good_parse)

    
    def good_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=GoodsparserItem(), response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('title', '//h1/text()')
        loader.add_xpath('cost', '//span[@slot="price"]/text()')
        loader.add_xpath('image_urls', '//picture[@slot="pictures"]/source[1]/@srcset')

        yield loader.load_item()