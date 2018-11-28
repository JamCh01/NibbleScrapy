import scrapy
import re
from bs4 import BeautifulSoup


class Chaziwang(scrapy.Spider):
    name = "chaziwang"
    allowed_domains = ['jitang.chaziwang.com']
    start_urls = ['http://jitang.chaziwang.com/']

    def __init__(self):
        self.content_regex = re.compile(r'cont')

    def parse(self, response):
        soup = BeautifulSoup(markup=response.text, features='lxml')
        box = soup.find(
            name='div', attrs={
                'id': 'container'
            }).find(
                name='div', attrs={'class': 'left'})
        items = box.find_all(name='div', attrs={'class': 'content'})
        for item in items:
            url = item.find(name='a')['href']
            yield scrapy.Request(
                url=response.urljoin(url), callback=self.parse_item)

        next_page = soup.find(
            name='div', attrs={
                'class': 'page center'
            }).find(
                name='a', text='下页')
        if next_page:
            next_url = next_page.get('href')
            # yield scrapy.Request(
            #     url=response.urljoin(next_url), callback=self.parse)

    def parse_item(self, response):
        soup = BeautifulSoup(markup=response.text, features='lxml')
        box = soup.find(name='div', attrs={'class': 'content'})
        content = box.find(
            name='div', attrs={
                'id': self.content_regex
            }).text.strip()
