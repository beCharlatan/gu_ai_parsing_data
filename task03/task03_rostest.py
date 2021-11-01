# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, которая будет добавлять только новые вакансии/продукты в вашу базу.

import requests
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient('127.0.0.1', 27017)
db = client['gu_ai_parsing_data_task_3']
coll = db.rostest_products

url = 'https://roscontrol.com'
route = '/testlab/search'
params = {
  'keyword': 'Хлеб',
  'page': 1
}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}

while True:
  response = requests.get(url + route, params=params, headers=headers)
  if response.ok:
    dom = bs(response.text, 'html.parser')

    page_products = dom.select('div.wrap-product-catalog__item')

    for page_product in page_products:
      product_data = {
        'title': None,
        'rating': {},
      }

      rating_total_score_node = page_product.find('div', {'class': ['rate']})

      product_data['source_url'] = url
      product_data['title'] = page_product.find('div', {'class': 'product__item-link'}).text
      product_data['_id'] = page_product.find('a', {'class': ['block-product-catalog__item']})['href'].split('/')[-2]

      if rating_total_score_node:
        if rating_total_score_node.text:
          product_data['rating']['total'] = int(rating_total_score_node.text)
          rating_scores = page_product.find('div', {'class': 'rating-block'}).findChildren('div', recursive=False)
          for rating_score in rating_scores:
            rating_label = rating_score.find('div', {'class': 'left'}).find('div', {'class': 'text'}).text
            product_data['rating'][rating_label] = int(rating_score.find('div', {'class': 'right'}).text)
        else:
          product_data['rating']['total'] = -1
          blacklist_node = page_product.find('div', {'class': 'rating-block'}).find('div', {'class': 'blacklist__item-danger'})
          product_data['rating']['Степень_нарушения'] = blacklist_node.find_all('span', {'class': ['def-text']})[1].text

      try:
          coll.insert_one(product_data)
      except DuplicateKeyError:
          pass

    print(f"Обработано страниц: {params['page']}")
    params['page'] += 1
  else:
    break


# 2. Для тех, кто выполнил задание с Росконтролем - напишите запрос для поиска продуктов с рейтингом не ниже введенного или качеством не ниже введенного (то есть цифра вводится одна, а запрос проверяет оба поля)
def get_products(score):
  products = coll.find({
    '$or': [
      {'rating.total': {'$gte': score}},
      {'rating.Качество': {'$gte': score}},
    ]
  })

  return products


products = get_products(75)

for product in products:
  print(product)
