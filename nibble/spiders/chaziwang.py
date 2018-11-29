import re
import scrapy
from bs4 import BeautifulSoup
from nibble.items import ContentItem


class Chaziwang(scrapy.Spider):
    name = "chaziwang"
    allowed_domains = ['jitang.chaziwang.com']
    start_urls = ['http://jitang.chaziwang.com/']

    def __init__(self):
        self.content_regex = re.compile(r'cont')
        self.suffix_regex = re.compile(r'- [\s\S]* - [\s\S]*')

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
            yield scrapy.Request(
                url=response.urljoin(next_url), callback=self.parse)

    def parse_item(self, response):
        item = ContentItem()
        soup = BeautifulSoup(markup=response.text, features='lxml')
        box = soup.find(name='div', attrs={'class': 'content'})
        content = box.find(
            name='div', attrs={
                'id': self.content_regex
            }).text.strip()
        content = self.suffix_regex.sub('', content)
        item['url'] = response.url
        item['content'] = content
        item['author'] = ''
        item['work'] = ''
        item['platform'] = 2
        item['status'] = 300
        yield item
