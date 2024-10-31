from psycopg2 import IntegrityError

from app import app
from log_utils import configure_logger
from models import Attachment, db

logger = configure_logger()


class SaveAttachmentsToDBPipeline:
    def process_item(self, item, spider):
        with app.app_context():  # Push app context for database interaction
            try:
                for attachment in item["attachments_meta"]:

                    # Check if the attachment already exists in the database
                    existing_item = (
                        db.session.query(Attachment)
                        .filter_by(attachment_url=attachment["url"])
                        .first()
                    )

                    if not existing_item:
                        db_attachment = item.attachment_model(attachment)
                        db.session.merge(db_attachment)

                db.session.commit()

            except IntegrityError:
                db.session.rollback()
                logger.error("Integrity constraint violation")
        return item
