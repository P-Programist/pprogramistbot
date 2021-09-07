import ssl
import re
import requests
import asyncio
import time
import schedule
from sqlalchemy.sql.expression import delete
from urllib3 import poolmanager
from bs4 import BeautifulSoup as BS
from database.models import (
    BishkekVacancy,
    engine,
    insert
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import delete

from configs.constants import BISHKEK_SCRAPER_URL as url


class TLSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLS,
            ssl_context=ctx)


session = requests.session()
session.mount('https://', TLSAdapter())


class Scraper:
    def __init__(self, url):
        main_html = self.get_html(url)
        self.soup = BS(main_html, 'html.parser')
        self.url = url

    def get_html(self, url):
        r = session.get(url)
        if r.status_code == 200:
            return r.text
        elif r.status_code == 403:
            print('Вы заблокированы на этом сайте!')
            return 0
        elif r.status_code == 404:
            print('Страница не найдена!')
            return 0

    def get_amount_of_pages(self):
        amount_of_pages = self.soup.find_all('a', class_='lb-orange-item page')
        max_page = int(max([i.text for i in amount_of_pages]))
        return max_page

    def get_data(self, max_page):
        data = []
        for page in range(1, max_page + 1):
            soup = BS(self.get_html(
                f'https://www.job.kg/it-work?page={page}'), 'html.parser')
            get_all = soup.find_all(
                'li', class_="vvl-one vvl-ord- vvl-detaled- show- hide-note-comment clearfix")
            if len(get_all) < 30:
                get_more = soup.find_all(
                    'li', class_="vvl-one vvl-ord- vvl-no-paid- vvl-detaled- show- hide-note-comment clearfix")
                get_all.extend(get_more)
            get_descriptions = soup.find_all(
                'a', class_='title-')
            address = [i.div.text.replace('\xa0', ' ').split('\n')[
                2] for i in get_all]
            salary = []
            for i in get_all:
                if not i.div.b:
                    salary.append('No data')
                else:
                    salary.append(i.div.b.text.replace('\xa0', ' '))
            headers = [i.text.replace('\xa0', ' ').split('\n')[
                15].strip() for i in get_all]
            details = [i['href'] for i in get_descriptions]
            descriptions = []
            company_names = []
            experience = []
            schedule = []
            for url in details:
                detail_soup = BS(self.get_html(
                    f'https://www.job.kg{url}'), 'html.parser')
                try:
                    descriptions.append(detail_soup.find(
                        'div', class_="details-").text.replace('\xa0', ' ').split('\n\n\n\n')[1].strip())
                except:
                    descriptions.append(detail_soup.find(
                        'div', class_="details-").text.replace('\xa0', ' ').strip())
                company_names.append(detail_soup.find(
                    'div', class_="employer- clearfix").p.b.a.text)
                elements_of_kasha = re.split(
                    '<dt>|</dt>|<dd>|</dd>', str(detail_soup.find('div', class_="vvloa-box").dl))
                if "Опыт" in elements_of_kasha:
                    experience.append(
                        elements_of_kasha[elements_of_kasha.index("Опыт")+2])
                else:
                    experience.append('не требуется.')
                if "График" in elements_of_kasha:
                    schedule.append(
                        elements_of_kasha[elements_of_kasha.index("График")+2])
                else:
                    schedule.append('Свободный график')

            for index in range(0, len(headers)):
                if address[index] == 'Кыргызстан: · Бишкек':
                    data.append(
                        (headers[index], company_names[index], experience[index], salary[index], schedule[index], descriptions[index]))
        return data


async def filling_database(scraper):

    async with engine.begin() as connection:
        cmd = delete(BishkekVacancy)
        await connection.execute(cmd)


    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin():
            for data in scraper.get_data(scraper.get_amount_of_pages()):
                if 'python' in data[5] or 'Python' in data[5]:
                    add_vacancy = insert(BishkekVacancy).values(
                        {
                            'header': data[0],
                            'company_name': data[1],
                            'required_experience': data[2],
                            'salary': data[3],
                            'schedule': data[4],
                            'details': data[5],
                            'type':'Python'
                        }
                    )
                    await session.execute(add_vacancy)
                elif 'javascript' in data[5] or 'JavaScript' in data[5] in data[5]:
                    add_vacancy = insert(BishkekVacancy).values(
                        {
                            'header': data[0],
                            'company_name': data[1],
                            'required_experience': data[2],
                            'salary': data[3],
                            'schedule': data[4],
                            'details': data[5],
                            'type':'JavaScript'
                        }
                    )
                    await session.execute(add_vacancy)
    await session.commit()
    return 'Good job!'


if __name__ == "__main__":
    scraper = Scraper(url)
    schedule.every(1).minutes.do(asyncio.run(filling_database(scraper)))

    while True:
        schedule.run_pending()

        time.sleep(5)
