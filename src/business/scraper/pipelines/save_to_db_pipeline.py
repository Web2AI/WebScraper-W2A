# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

from psycopg2 import IntegrityError

from app import app
from log_utils import configure_logger
from models import db

logger = configure_logger()


class SaveToDBPipeline:
    def process_item(self, item, spider):
        with app.app_context():  # Push app context for database interaction
            try:
                db_item = item.model
                db.session.merge(db_item)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                logger.error("Integrity constraint violation")
        return item
