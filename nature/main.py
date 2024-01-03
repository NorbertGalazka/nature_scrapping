from bs4 import BeautifulSoup
from dataclasses import dataclass
import aiohttp
import asyncio


@dataclass
class Article:
    title: str
    author: str
    description: str
    date: str


async def get_max_page(soup):
    raw_list_of_pages = []
    processed_list = []
    max_page_soup = soup.find_all(class_='c-pagination__item')
    for element in max_page_soup:
        try:
            raw_list_of_pages.append(element['data-page'])
        except KeyError:
            continue
    for element in raw_list_of_pages:
        try:
            processed_list.append(int(element))
        except ValueError:
            continue

    return max(processed_list)


async def get_all_html_code(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html_code = await response.text()
                return BeautifulSoup(html_code, 'html.parser')
    return None


async def get_all_articles_from_site(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            html_code = await response.text()
            soup = BeautifulSoup(html_code, 'html.parser')
            articles_from_site = None
            content = soup.find('ul', class_='ma0 mb-negative-2 clean-list')
            if content:
                articles_from_site = content.find_all('li', class_='border-gray-medium border-bottom-1 pb20 mt20')
            return articles_from_site
    return None


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


async def main():
    subjects = ['physical-sciences', 'earth-and-environmental-sciences',
                'biological-sciences', 'health-sciences', 'scientific-community-and-society']

    article_objects = []

    async with aiohttp.ClientSession() as session:
        for subject in subjects:
            basic_url = f'https://www.nature.com/subjects/{subject}/nature?searchType=journalSearch&sort=PubDate&page=1'
            max_page = await get_max_page(await get_all_html_code(url=basic_url))

            tasks = []
            for page in range(max_page):
                url = f'https://www.nature.com/subjects/{subject}/nature?searchType=journalSearch&sort=PubDate&page={page + 1}'
                print(f'pobieram artykuły {subject} ze strony {page + 1}')

                tasks.append(get_all_articles_from_site(session, url))

            articles_pages = await asyncio.gather(*tasks)

            for articles_in_single_page in articles_pages:
                if articles_in_single_page:
                    for article_in_single_page in articles_in_single_page:
                        article_objects.append(get_article_data(article_in_single_page))

    for article_obj in article_objects:
        print(article_obj.date, article_obj.title)

if __name__ == "__main__":
    asyncio.run(main())

