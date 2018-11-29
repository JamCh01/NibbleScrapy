# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import redis
from hashlib import md5
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from nibble.tables import ContentTemplate
from scrapy.exceptions import DropItem
from nibble.static import MYSQL_CONNECTION, REDIS_CONEECTION


class SimpleHash(object):
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter(object):
    def __init__(self, blockNum=1, key='bloomfilter'):
        self.pool = redis.ConnectionPool(**REDIS_CONEECTION)
        self.server = redis.Redis(connection_pool=self.pool)
        self.bit_size = 1 << 31
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.key = key
        self.blockNum = blockNum
        self.hashfunc = []
        for seed in self.seeds:
            self.hashfunc.append(SimpleHash(self.bit_size, seed))

    def get_item(self, str_input):
        if not str_input:
            return False
        m5 = md5()
        m5.update(str_input.encode('utf8'))
        str_input = m5.hexdigest()
        ret = True
        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        for f in self.hashfunc:
            loc = f.hash(str_input)
            ret = ret & self.server.getbit(name, loc)
        return ret

    def set_item(self, str_input):
        m5 = md5()
        m5.update(str_input.encode('utf8'))
        str_input = m5.hexdigest()
        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        for f in self.hashfunc:
            loc = f.hash(str_input)
            self.server.setbit(name, loc, 1)


class DuplicatesPipeline(object):
    def __init__(self):
        self.filter = BloomFilter()
        self.punctuation_regex = re.compile(
            r'[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*（）]+')

    def process_item(self, item, spider):
        content = self.punctuation_regex.sub('', item['content'])
        if self.filter.get_item(str_input=item['url']) or self.filter.get_item(
                str_input=content):
            raise DropItem("Duplicate item found: %s" % item)

        else:
            self.filter.set_item(str_input=item['url'])
            self.filter.set_item(str_input=content)
            return item


class ContentPipeline(object):
    def __init__(self):
        self.engine = create_engine(MYSQL_CONNECTION, echo=False)
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
