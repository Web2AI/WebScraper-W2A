# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

from app import app


class SaveToDBPipeline:
    def process_item(self, item, spider):
        with app.app_context():  # Push app context for database interaction
            item.save_to_db()
        return item
