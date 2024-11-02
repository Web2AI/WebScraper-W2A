import scrapy

from models import Attachment


class AttachmentItem(scrapy.Item):
    type = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    site_url = scrapy.Field()

    @property
    def model(self):
        return Attachment(
            id=None,  # Auto-generated primary key
            site_url=self["site_url"],
            type=self["type"],
            content=self["content"],
            url=self["url"],
        )
