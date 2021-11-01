# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, которая будет добавлять только новые вакансии/продукты в вашу базу.

import requests
import re
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient('127.0.0.1', 27017)
db = client['gu_ai_parsing_data_task_3']
coll = db.hh_vacancies

# Взято из 2 задания
url = 'https://hh.ru'
route = '/search/vacancy'
params = {
  'text': 'frontend',
  'page': 0
}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}

while True:
  response = requests.get(url + route, params=params, headers=headers)
  if response.ok:
    dom = bs(response.text, 'html.parser')

    page_vacancies = dom.select('div.vacancy-serp-item')

    if not page_vacancies:
      break

    for page_vacancy in page_vacancies:
      vacancy_data = {
        'salary_from': None,
        'salary_to': None,
        'salary_currency': None
      }

      link_node = page_vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
      salary_node = page_vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})

      vacancy_data['title'] = link_node.text
      vacancy_data['url'] = link_node['href']
      vacancy_data['from'] = url

      vacancy_data['_id'] = link_node['href'].split('/')[-1].split('?')[0]

      if salary_node:
        salary_list = re.sub('\u202f', '', salary_node.text).split()
        vacancy_data['salary_currency'] = salary_list.pop()

        if salary_list[0] == 'от':
          vacancy_data['salary_from'] = int(salary_list[1])
          if 'до' in salary_list:
            vacancy_data['salary_to'] = int(salary_list[3])
        elif salary_list[0] == 'до':
          vacancy_data['salary_to'] = int(salary_list[1])
        else:
          vacancy_data['salary_from'] = int(salary_list[0])
          if '–' in salary_list:
            vacancy_data['salary_from'] = int(salary_list[0])
            vacancy_data['salary_to'] = int(salary_list[2])
          else:
            vacancy_data['salary_to'] = int(salary_list[0])

      try:
          coll.insert_one(vacancy_data)
      except DuplicateKeyError:
          pass

    print(f"Обработано страниц: {params['page'] + 1}")
    params['page'] += 1
  else:
    break


# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы (необходимо анализировать оба поля зарплаты)
def get_vacancies(min_salary):
  vacancies = coll.find(
    # {'salary_from': {'$gt': min_salary}, 'salary_to': {'$gt': min_salary}}
    {'$or': [
      {'salary_from': {'$gt': min_salary}},
      {'salary_to': {'$gt': min_salary}}
    ]}
  )
  return vacancies


vacancies = get_vacancies(100000)

for vacancy in vacancies:
  print(vacancy)
