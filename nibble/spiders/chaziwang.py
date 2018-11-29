import re
import scrapy
import hashlib
from bs4 import BeautifulSoup
from nibble.items import ContentItem


class Chaziwang(scrapy.Spider):
    name = "chaziwang"
    allowed_domains = ['jitang.chaziwang.com']
    start_urls = ['http://jitang.chaziwang.com/']

    def __init__(self):
        self.content_regex = re.compile(r'cont')
        self.suffix_regex = re.compile(r'- [\s\S]* - [\s\S]*')
        self.punctuation_regex = re.compile(
            r'[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*（）]+')

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
        url = response.url
        url_hash = hashlib.md5(url.encode('utf8')).hexdigest()
        item = ContentItem()
        soup = BeautifulSoup(markup=response.text, features='lxml')
        box = soup.find(name='div', attrs={'class': 'content'})
        content = box.find(
            name='div', attrs={
                'id': self.content_regex
            }).text.strip()
        content = self.suffix_regex.sub('', content)
        content_without_punctuation = self.punctuation_regex.sub('', content)
        content_hash = hashlib.md5(
            content_without_punctuation.encode('utf8')).hexdigest()
        item['url'] = url
        item['content'] = content
        item['author'] = ''
        item['content_hash'] = content_hash
        item['url_hash'] = url_hash
        item['work'] = ''
        item['platform'] = 2
        item['status'] = 300
        yield item
