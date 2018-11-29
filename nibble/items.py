# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ContentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    content_hash = scrapy.Field()
    url_hash = scrapy.Field()
    work = scrapy.Field()
    platform = scrapy.Field()
    status = scrapy.Field()