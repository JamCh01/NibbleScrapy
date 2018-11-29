# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from nibble.tables import ContentTemplate
from nibble.static import MYSQL_CONNECTION


class ContentPipeline(object):
    def __init__(self):
        self.engine = create_engine(MYSQL_CONNECTION, echo=True)
        _ = sessionmaker(bind=self.engine)
        self.session = _()
        Base = declarative_base()
        self.content = type('content', (Base, ContentTemplate),
                            {'__tablename__': 'content'})

    def process_item(self, item, spider):
        self.session.add(self.content(**item))
        self.session.commit()

    def close_spider(self, spider):
        self.session.close()
