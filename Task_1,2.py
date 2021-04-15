import pprint
import requests
from lxml import html
from bs4 import BeautifulSoup
from pymongo import MongoClient

def get_html(url):
    r = requests.get(url)
    return r.text

def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find('div', class_='pagination-pages clearfix')
    pages = divs.find_all('a', class_='pagination-page')[-1].get('href')
    total_pages = pages.split('=')[1].split('&')[0]
    return int(total_pages)

def request_to_site():
    headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    }
    params = {
        'text': 'Data+engineer'
    }
    try:
        request = requests.get('https://hh.ru/search/vacancy', headers=headers, params=params)
        return request.text
    except requests.exceptions.ConnectionError:
        print('Please check your internet connection!')
        exit(1)

def save_to_mongo_db():
    client = MongoClient('localhost', 27017)
    db = client['hh']
    vacancies_db = db.vacancies
    vacancies_db.drop()

    html_page = html.fromstring(request_to_site())
    vacancies = html_page.xpath("//div[contains(@class, 'item__row_header')]")
    for vacancy in vacancies:
        try:
            salary = vacancy.xpath('.//div[contains(@class, "item__compensation")]/text()')[0]
        except IndexError:
            salary = 'no information about a salary'
        data_vacancy = {
            "title": vacancy.xpath('.//a/text()')[0],
            "link": vacancy.xpath('.//a/@href')[0],
            "salary": salary
        }
        vacancies_db.insert_one(data_vacancy)
        print('Added')


def search_by_salary(vacancies_db):
    try:
        salary = int(input('\nEnter: '))
    except ValueError:
        print('Error.')
        exit(1)
    db = vacancies_db.find({'salary': {'$gt': salary}})
    for _ in db:
        pprint.pprint(_)


save_to_mongo_db() 