# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime
import logging
import os
from pathlib import Path

from app import app
from scraper.items.site_item import SiteItem

logger = logging.getLogger()


class SaveToHtmlFilePipeline:
    def process_item(self, item, spider):
        with app.app_context():
            if not item.should_save():
                return item

        if isinstance(item, SiteItem):

            logger.debug(f"Saving {item["url"]} to file")

            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            project_dir = os.getenv("PROJECT_DIR")
            output_dir = Path(project_dir, "out").resolve()
            filename = f"{item.get('url').replace('/','')}-{timestamp}.html"

            os.makedirs(os.path.dirname(output_dir), exist_ok=True)
            with open(Path(output_dir, filename), "w") as f:
                f.write(item.get("html"))

        return item
