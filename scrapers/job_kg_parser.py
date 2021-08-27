from urllib3 import poolmanager
import ssl
import requests
from bs4 import BeautifulSoup as BS


url = 'https://www.job.kg'


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
            salary = [i.div.b.text.replace('\xa0', ' ') for i in get_all]
            headers = [i.text.replace('\xa0', ' ').split('\n')[
                15].strip() for i in get_all]
            details = [i['href'] for i in get_descriptions]
            descriptions = []
            for url in details:
                detail_soup = BS(self.get_html(
                    f'https://www.job.kg{url}'), 'html.parser')
                try:
                    descriptions.append(detail_soup.find(
                        'div', class_="details-").text.replace('\xa0', ' ').split('\n\n\n\n')[1].strip())
                except:
                    descriptions.append(detail_soup.find(
                        'div', class_="details-").text.replace('\xa0', ' ').strip())
            for index in range(0, len(salary)):
                if address[index] == 'Кыргызстан: · Бишкек':
                    data.append(
                        (headers[index], descriptions[index], salary[index]))
        return data


if __name__ == "__main__":
    scraper = Scraper('https://www.job.kg/it-work')
    for line in scraper.get_data(scraper.get_amount_of_pages()):
        print(line)
