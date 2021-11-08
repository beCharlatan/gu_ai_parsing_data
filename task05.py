# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import time

client = MongoClient('127.0.0.1', 27017)
db = client['gu_ai_parsing_data_task_5']
coll = db.mail_letters

driver = webdriver.Chrome(executable_path="chromedriver.exe")

driver.get("https://mail.ru")
actions = ActionChains(driver)

# LOGIN
login = driver.find_element(By.NAME, 'login')
login.send_keys('<enter your login>')

_btn = driver.find_element(By.XPATH, '//button[@data-testid="enter-password"]')
_btn.click()

time.sleep(1)

password = driver.find_element(By.NAME, 'password')
password.send_keys('<enter your password>')

_btn = driver.find_element(By.XPATH, '//button[@data-testid="login-to-mail"]')
_btn.click()
# LOGIN

time.sleep(5)

# STORE LETTER URLS
urls = []
lastUrl = None

while True:
  page_letters = driver.find_elements(By.XPATH, '//a[contains(@class, "js-letter-list-item")]')
  lastLetterPerPage = page_letters[-1]
  lastUrlPerPage = lastLetterPerPage.get_attribute('href')

  if lastUrl == lastUrlPerPage:
    break

  for letter in page_letters:
    urls.append(letter.get_attribute('href'))

  lastUrl = lastUrlPerPage
  actions.move_to_element(lastLetterPerPage).perform()

  time.sleep(3)
# STORE LETTER URLS

print()

# STORE LETTER DATA
for url in urls:
  driver.get(url)
  time.sleep(2)
  fromBlock = driver.find_element(By.XPATH, '//span[contains(@class, "letter-contact")]')
  whenBlock = driver.find_element(By.XPATH, '//div[contains(@class, "letter__date")]')
  subjectBlock = driver.find_element(By.XPATH, '//h2[contains(@class, "thread__subject")]')
  bodyBlock = driver.find_element(By.XPATH, '//div[contains(@class, "letter-body__body-content")]')

  try:
    coll.insert_one({
      "_id": url,
      "from": fromBlock.get_attribute("title"),
      "when": whenBlock.text,
      "subject": subjectBlock.text,
      "body": bodyBlock.text
    })
  except DuplicateKeyError:
      pass
# STORE LETTER DATA
