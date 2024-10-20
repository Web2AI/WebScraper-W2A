# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime
from itemadapter import ItemAdapter

class SaveToHtmlFilePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"pcss-{adapter.get('url')}-{timestamp}.html"

        with open(filename, "w") as f:
            f.write(adapter.get('html'))

        return item
