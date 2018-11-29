# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Text


class ContentTemplate():
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    url = Column(Text)
    author = Column(String(50))
    work = Column(String(50))
    status = Column(Integer)
    tags = Column(Text)
    platform = Column(Integer)

    def __init__(self, **items):
        for key in items:
            if hasattr(self, key):
                setattr(self, key, items[key])
