# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import datetime

import scrapy
from sqlalchemy.exc import IntegrityError

from log_utils import configure_logger
from models import Site, db

logger = configure_logger()


class StrippedHtmlItem(scrapy.Item):
    url = scrapy.Field()
    html = scrapy.Field()
    json = scrapy.Field()

    def save_to_db(self):
        try:
            db_item = Site(
                url=self["url"], json=self["json"], date=datetime.datetime.now()
            )
            db.session.merge(db_item)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            logger.error("Integrity constraint violation")
