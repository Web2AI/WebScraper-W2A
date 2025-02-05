from functools import cached_property

import scrapy

from models import AttachmentModel
from scraper.items.base_item import BaseItem


class AttachmentItem(BaseItem):
    type = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    site_item = scrapy.Field()

    @property
    def model(self):
        return AttachmentModel(
            id=None,  # Auto-generated primary key
            site_url=self.get("site_item").get("url"),
            type=self.get("type"),
            content=self.get("content"),
            url=self.get("url"),
        )

    @cached_property
    def should_save(self):
        return self.get("site_item").should_save
