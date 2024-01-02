from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass


@dataclass
class Article:
    title: str
    author: str
    description: str
    date: str


def get_all_html_code(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    return None


def get_all_articles_from_site(soup):
    articles_from_site = None

    content = soup.find('ul', class_= 'ma0 mb-negative-2 clean-list')

    if content:
        articles_from_site = content.find_all('li', class_='border-gray-medium border-bottom-1 pb20 mt20')

    return articles_from_site


def get_article_data(article):
    title = article.find('a', class_='text-gray').text.strip()
    description_soup = article.find('div', itemprop="description")
    if description_soup:
        description = description_soup.find('p').text
    else:
        description = None
    date = article.find('time')['datetime']
    author_soup = article.find('span', itemprop='name')
    if author_soup:
        author = author_soup.text
    else:
        author = None

    return Article(title=title, author=author, date=date, description=description)


url = 'https://www.nature.com/subjects/earth-and-environmental-sciences/nature'

articles = get_all_articles_from_site(get_all_html_code(url=url))

article_objects = []

for article in articles:
    article_objects.append(get_article_data(article))

for article_obj in article_objects:
    print(article_obj.date, article_obj.title)

