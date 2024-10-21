import datetime
import logging
import os

import scrapy
from bs4 import BeautifulSoup

from business.web2ai.items import StrippedHtmlItem


class PcssSpider(scrapy.Spider):
    name = "pcss"

    def __init__(self, url, request_id, **kwargs):
        self.url = url
        self.request_id = request_id
        self.logger.debug(f"Spider initialized with request_id: {self.request_id}")
        super().__init__(**kwargs)

    custom_settings = {
        "CLOSESPIDER_TIMEOUT": 15,
    }  # This will tell scrapy to store the scraped data to outputfile.json and for how long the spider should run.

    def stripTags(self, response):
        # Use BeautifulSoup to clean the HTML
        soup = BeautifulSoup(response.body, "html.parser")

        # Remove script and style tags
        for tag in soup(["script", "style", "head", "link"]):
            tag.decompose()  # Remove the tag and its content

        # # Optionally remove elements with 'nav' in id or class
        # for tag in soup.find_all(id=lambda x: x and "nav" in x):
        #     tag.decompose()

        # for tag in soup.find_all(class_=lambda x: x and "nav" in x):
        #     tag.decompose()

        # Return the cleaned HTML as a string (not bytes)
        return soup.prettify()

    def start_requests(self):
        request = scrapy.Request(self.url, callback=self.parse)
        yield request

    def parse(self, response):
        item = StrippedHtmlItem()
        item["html"] = self.stripTags(response)
        item["url"] = response.url.split("/")[2]

        # Log the scraped URL and HTML length for debugging
        self.logger.debug(f"Scraped URL: {item["url"]}")
        self.logger.debug(f"HTML Length: {len(item["html"])}")

        # Save the HTML to a file
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"out/TEST-{item['url']}-{timestamp}.html"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(item["html"])

        # Optionally yield the item to trigger the pipeline
        yield item
