# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import datetime
import logging
from functools import cached_property

import scrapy

from models import SiteModel
from scraper.items.base_item import BaseItem

logger = logging.getLogger()


class SiteItem(BaseItem):
    url = scrapy.Field()
    parent_url = scrapy.Field()
    html = scrapy.Field()
    json = scrapy.Field()
    attachments_meta = scrapy.Field()
    page_hash = scrapy.Field()

    @property
    def model(self):
        return SiteModel(
            url=self.get("url"),
            parent_url=self.get("parent_url"),
            json=self.get("json"),
            date=datetime.datetime.now(),
            page_hash=self.get("page_hash"),
        )

    @cached_property
    def should_save(self):
        existing_item = SiteModel.query.get(self.get("url"))
        if existing_item is not None and existing_item.page_hash == self.get(
            "page_hash"
        ):
            return False

        return True
