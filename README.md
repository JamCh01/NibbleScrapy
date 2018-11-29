# Nibbles
Nibbles的爬虫模块，使用Scrapy构建。旨在抓取公开在互联网上的一句话和图片。

# 如何使用  
在```nibble```目录下增加```static.py```，增加自己的数据库信息，如：
```python
MYSQL_CONNECTION = 'mysql+pymysql://root:test@127.0.0.1:3306/nibbles?charset=utf8'
REDIS_CONEECTION = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 14,
    'password': '',
}
```
