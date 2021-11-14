from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from spiders.labirint import LabirintSpider
import settings

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(crawler_settings)
    process.crawl(LabirintSpider)
    process.start()
