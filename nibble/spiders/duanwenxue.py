import re
import scrapy
import hashlib
from bs4 import BeautifulSoup
from nibble.items import ContentItem


class Duanwenxue(scrapy.Spider):
    name = "duanwenxue"
    allowed_domains = ['www.duanwenxue.com']
    start_urls = ['https://www.duanwenxue.com/yulu/yijuhua/']

    def __init__(self):
        self.punctuation_regex = re.compile(
            r'[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*（）]+')

    def parse(self, response):
        soup = BeautifulSoup(markup=response.text, features='lxml')
        box = soup.find(name='div', attrs={'class': 'list-short-article'})
        items = box.find_all(name='li')
        for item in items:
            url = item.find(name='a')['href']
            yield scrapy.Request(
                url=response.urljoin(url), callback=self.parse_item)

        next_page = soup.find(
            name='div', attrs={
                'class': 'list-pages'
            }).find(
                name='a', text='下一页')
        if next_page:
            next_url = next_page.get('href')
            yield scrapy.Request(
                url=response.urljoin(next_url), callback=self.parse)

    def parse_item(self, response):
        url = response.url
        url_hash = hashlib.md5(url.encode('utf8')).hexdigest()
        item = ContentItem()
        soup = BeautifulSoup(markup=response.text, features='lxml')
        try:
            soup.find(name='span', attrs={'id': 'audio-span'}).decompose()
        except Exception:
            pass
        content = ''.join(
            soup.find(name='div', attrs={
                'class': 'article-content'
            }).find(name='p', attrs=False).text.strip().split())
        content_without_punctuation = self.punctuation_regex.sub('', content)
        content_hash = hashlib.md5(
            content_without_punctuation.encode('utf8')).hexdigest()
        item['content'] = content
        item['url'] = url
        item['author'] = ''
        item['content_hash'] = content_hash
        item['url_hash'] = url_hash
        item['work'] = ''
        item['platform'] = 2
        item['status'] = 300
        yield item
