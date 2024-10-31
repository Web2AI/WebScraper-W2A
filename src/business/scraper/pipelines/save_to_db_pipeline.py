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

logger = logging.getLogger(__name__)


class SaveToDBPipeline:
    def process_item(self, item, spider):
        with app.app_context():  # Push app context for database interaction
            try:

                if item is None:
                    logger.error("Received None item, skipping...")
                    return

                db_item = item.model
                db.session.merge(db_item)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                logger.error("Integrity constraint violation")

        return item
