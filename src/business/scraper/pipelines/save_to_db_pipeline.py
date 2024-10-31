# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

from psycopg2 import IntegrityError

from app import app
from log_utils import configure_logger
from models import Attachment, Site, db

logger = configure_logger()


class SaveToDBPipeline:
    def process_item(self, item, spider):
        with app.app_context():  # Push app context for database interaction
            try:

                if item is None:
                    logger.error("Received None item, skipping...")
                    return

                db_item = item.model
                if isinstance(db_item, Site):
                    existing_item = Site.query.get(item["url"])
                    if existing_item is None:
                        db.session.add(db_item)
                        db.session.commit()
                    elif existing_item.page_hash != item["page_hash"]:
                        db.session.merge(db_item)
                        db.session.commit()
                if isinstance(db_item, Attachment):
                    db.session.merge(db_item)
                    db.session.commit()
            except IntegrityError:
                db.session.rollback()
                logger.error("Integrity constraint violation")

        return item
