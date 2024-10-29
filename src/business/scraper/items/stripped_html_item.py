# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import datetime

import scrapy

from models import Site, db


class StrippedHtmlItem(scrapy.Item):
    url = scrapy.Field()
    html = scrapy.Field()
    json = scrapy.Field()

    def save_to_db(self):
        # model_data = {field: self.get(field) for field in self.fields}
        # db_item = Site(**model_data, date=datetime.datetime.now())
        db_item = Site(url=self["url"], json=self["json"], date=datetime.datetime.now())
        db.session.add(db_item)
        db.session.commit()
