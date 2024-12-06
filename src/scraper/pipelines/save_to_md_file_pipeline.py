# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime
import logging
import os
import re
from pathlib import Path

import markdownify as md

from app import app
from scraper.items.site_item import SiteItem

logger = logging.getLogger()


class SaveToMdFilePipeline:

    # Remove multiple newlines
    def remove_newlines(self, md_text):
        return re.sub(r"\n\s*\n+", "\n\n", md_text)

    def process_item(self, item, spider):
        if not isinstance(item, SiteItem):
            return item

        with app.app_context():
            if not item.should_save:
                return item

        logger.debug(f"Saving {item["url"]} to .md file")

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        project_dir = os.getenv("PROJECT_DIR")
        output_dir = Path(project_dir, "out", "md_files").resolve()
        filename = f"{item.get('url').replace('/','')}-{timestamp}.md"

        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        md_text = md.markdownify(item.get("html"), heading_style="ATX")
        md_text = self.remove_newlines(md_text)

        with open(Path(output_dir, filename), "w") as f:
            f.write(md_text)

        return item
