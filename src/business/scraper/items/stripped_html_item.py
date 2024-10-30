# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import datetime

import scrapy

from log_utils import configure_logger
from models import Site

logger = configure_logger()


class StrippedHtmlItem(scrapy.Item):
    url = scrapy.Field()
    html = scrapy.Field()
    json = scrapy.Field()

    @property
    def model(self):
        return Site(url=self["url"], json=self["json"], date=datetime.datetime.now())
