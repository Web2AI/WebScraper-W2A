# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime
import logging
import os

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
            output_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "~/out")
            )  # TODO: figure out a way to make this path absolute, not relative
            filename = (
                f"{output_dir}/pcss-{item.get('url').replace('/','')}-{timestamp}.html"
            )

            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write(item.get("html"))

        return item
