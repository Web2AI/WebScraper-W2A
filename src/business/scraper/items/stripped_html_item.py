# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import datetime

import scrapy

from models import Site


class StrippedHtmlItem(scrapy.Item):
    url = scrapy.Field()
    parent_url = scrapy.Field()
    html = scrapy.Field()
    json = scrapy.Field()
    attachments_meta = scrapy.Field()
    page_hash = scrapy.Field()

    @property
    def model(self):
        return Site(
            url=self["url"],
            parent_url=self["parent_url"],
            json=self["json"],
            date=datetime.datetime.now(),
            page_hash=self["page_hash"],
        )
