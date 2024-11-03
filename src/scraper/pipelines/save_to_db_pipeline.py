# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

import logging

from psycopg2 import IntegrityError

from app import app
from models import db
from scraper.items.base_item import BaseItem

logger = logging.getLogger()


class SaveToDBPipeline:
    def process_item(self, item: BaseItem, spider):
        if item is None:
            logger.error("Received None item, skipping...")
            return item

        with app.app_context():
            try:
                if not item.should_save():
                    return item

                logger.debug(f"Saving {item["url"]} to db")

                db.session.merge(item.model)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                logger.error("Integrity constraint violation")

        return item
