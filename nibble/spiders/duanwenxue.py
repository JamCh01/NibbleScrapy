import scrapy
from bs4 import BeautifulSoup


class Duanwenxue(scrapy.Spider):
    name = "duanwenxue"
    allowed_domains = ['www.duanwenxue.com']
    start_urls = ['https://www.duanwenxue.com/yulu/yijuhua/']

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
        soup = BeautifulSoup(markup=response.text, features='lxml')
        try:
            soup.find(name='span', attrs={'id': 'audio-span'}).decompose()
        except Exception:
            pass
        content = soup.find(
            name='div', attrs={
                'class': 'article-content'
            }).find(
                name='p', attrs=False).text
        print(response.url)
        print(content)
