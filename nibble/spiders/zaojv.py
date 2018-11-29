import re
import scrapy
import hashlib
from bs4 import BeautifulSoup
from nibble.items import ContentItem


class Zaojv(scrapy.Spider):
    name = "zaojv"
    allowed_domains = ['zaojv.com']
    start_urls = ['http://zaojv.com/wordmj.html']

    def __init__(self):
        self.punctuation_regex = re.compile(
            r'[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*（）]+')

    def parse(self, response):
        soup = BeautifulSoup(markup=response.text, features='lxml')
        box = soup.find(name='div', attrs={'id': 'div_content'})
        items = box.find_all(name='div', attrs={'id': 'div_left'})
        for item in items:
            authors = item.find_all(name='li', attrs={'class': 'dotline'})
            for author in authors:
                url = author.find(name='a').get('href')
                author = author.find(name='a').text
                response.meta.update(author=author)
                yield scrapy.Request(
                    url=response.urljoin(url),
                    callback=self.parse_item,
                    meta=dict(author=author))

        next_page = soup.find(
            name='div', attrs={
                'style': 'text-align:center;margin-top:10px;'
            }).find(
                name='a', text='下一页')
        if next_page:
            next_url = next_page.get('href')
            yield scrapy.Request(
                url=response.urljoin(next_url), callback=self.parse)

    def parse_item(self, response):
        soup = BeautifulSoup(markup=response.text, features='lxml')
        items = soup.find(
            name='div', attrs={
                'id': 'all'
            }).find_all(
                name='div', attrs={'id': False})
        for item in items:
            try:
                url = item.find(name='a').get('href')
                yield scrapy.Request(
                    url=response.urljoin(url),
                    callback=self.parse_content,
                    meta=response.meta)
            except Exception:
                pass

    def parse_content(self, response):
        url = response.url
        url_hash = hashlib.md5(url.encode('utf8')).hexdigest()
        item = ContentItem()
        soup = BeautifulSoup(markup=response.text, features='lxml')
        content = ''.join(
            soup.find(name='td', attrs={
                'style': 'padding-bottom:15px;'
            }).text.strip().split())
        content_without_punctuation = self.punctuation_regex.sub('', content)
        content_hash = hashlib.md5(
            content_without_punctuation.encode('utf8')).hexdigest()
        item['url'] = response.url
        item['content'] = content
        item['author'] = response.meta.get('author')
        item['content_hash'] = content_hash
        item['url_hash'] = url_hash
        item['work'] = ''
        item['platform'] = 2
        item['status'] = 300
        yield item
