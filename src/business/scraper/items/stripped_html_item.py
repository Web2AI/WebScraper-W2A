# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import datetime

import scrapy

from log_utils import configure_logger
from models import Attachment, Site

logger = configure_logger()


class StrippedHtmlItem(scrapy.Item):
    url = scrapy.Field()
    parent_url = scrapy.Field()
    html = scrapy.Field()
    json = scrapy.Field()
    attachments_meta = scrapy.Field()

    @property
    def model(self):
        return Site(
            url=self["url"],
            parent_url=self["parent_url"],
            json=self["json"],
            date=datetime.datetime.now(),
        )
    
    def attachment_model(self, attachment):
        return Attachment(
            id=None,  # Auto-generated primary key
            url=self["url"],
            attachment_type=attachment["type"],
            attachment_content=attachment["content"],
            attachment_url=attachment["url"],
        )