# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime
import os

from itemadapter import ItemAdapter


class SaveToHtmlFilePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../../out")
        )
        filename = f"{output_dir}/pcss-{adapter.get('url')}-{timestamp}.html"

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(adapter.get("html"))

        return item
