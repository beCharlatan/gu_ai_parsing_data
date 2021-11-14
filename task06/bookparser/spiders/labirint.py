import scrapy
from scrapy.http import HtmlResponse
from items import BookparserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = [
        'https://www.labirint.ru/genres/1850/', # Книги для детей
        'https://www.labirint.ru/genres/2993/' # Комиксы, манга, артбуки
    ]

    def parse(self, response: HtmlResponse):
        next_url = response.xpath('//div[@class="pagination-next"]/a/@href').get()
        if next_url:
            yield response.follow(next_url, callback=self.parse)

        book_links = response.xpath('//div[@id="catalog"]//a[@class="product-title-link"]/@href').getall()
        for book_link in book_links:
            yield response.follow(book_link, callback=self.book_parse)

    
    def book_parse(self, response: HtmlResponse):
        url = response.url
        title = response.xpath('//h1/text()').get()
        authors = response.xpath('//div[@class="authors"]/a/text()').getall()
        cost = response.xpath('//span[contains(@class, "val-number")]/text()').getall()
        rating = response.xpath('//div[@id="rate"]/text()').get()

        yield BookparserItem(url=url, title=title, authors=authors, cost=cost, rating=rating)