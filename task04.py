# 1. Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
# - название источника;
# - наименование новости;
# - ссылку на новость;
# - дата публикации.
# 2. Сложить собранные новости в БД

import requests
from urllib.parse import urlparse
from urllib.parse import parse_qs
from lxml import html
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient('127.0.0.1', 27017)
db = client['gu_ai_parsing_data_task_4']
coll = db.yandex_news

url = 'https://yandex.ru/news/'

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'}

response = requests.get(url)

dom = html.fromstring(response.text)

items = dom.xpath("//article[contains(@class,'mg-card')]")

for item in items:
    data = {}

    title = item.xpath(".//h2[contains(@class,'mg-card__title')]/text()")
    url = item.xpath(".//a[contains(@class,'mg-card__link')]/@href")
    source = item.xpath(".//a[contains(@class,'mg-card__source-link')]/text()")
    time = item.xpath(".//span[contains(@class,'mg-card-source__time')]/text()")

    parsed_url = urlparse(url[0])
    # persistent_id
    # Это у яндекса непосредственный идентификатор новости в параметрах запроса в урле на новость
    idx = parse_qs(parsed_url.query)['persistent_id'][0]

    data['_id'] = idx
    data['title'] = title[0]
    data['url'] = url[0]
    data['source'] = source[0]
    data['time'] = time[0]

    try:
        coll.insert_one(data)
    except DuplicateKeyError:
        pass
