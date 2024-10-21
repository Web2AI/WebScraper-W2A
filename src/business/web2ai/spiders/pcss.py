import datetime
import logging
import os

import scrapy
from bs4 import BeautifulSoup

from business.web2ai.html_filter import HtmlFilter
from business.web2ai.items import StrippedHtmlItem

logger = logging.getLogger()


class PcssSpider(scrapy.Spider):
    name = "pcss"

    def __init__(self, primary_url, secondary_url, request_id, **kwargs):
        self.primary_url = primary_url
        self.secondary_url = secondary_url
        self.request_id = request_id
        self.primary_data = None
        self.secondary_data = None
        logger.debug(f"Spider initialized with request_id: {self.request_id}")
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
        # Request the primary URL
        logger.debug(f"Starting request for primary URL: {self.primary_url}")
        yield scrapy.Request(self.primary_url, callback=self.parse_primary)

        # Request the secondary URL
        if self.secondary_url:
            logger.debug(f"Starting request for secondary URL: {self.secondary_url}")
            yield scrapy.Request(self.secondary_url, callback=self.parse_secondary)

    def parse(self, response):
        item = StrippedHtmlItem()
        item["html"] = self.stripTags(response)
        item["url"] = response.url.split("/")[2]

        # Log the scraped URL and HTML length for debugging
        logger.debug(f"Scraped URL: {item["url"]}")
        logger.debug(f"HTML Length: {len(item["html"])}")

        # Save the HTML to a file
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"out/TEST-{item['url']}-{timestamp}.html"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(item["html"])

        # Optionally yield the item to trigger the pipeline
        yield item

    def parse_primary(self, response):
        logger.debug(f"Parsing response from primary URL: {response.url}")
        item = StrippedHtmlItem()
        item["html"] = self.stripTags(response)
        item["url"] = response.url.split("/")[2]

        # Log the scraped primary URL and HTML length
        logger.debug(f"Primary URL: {item['url']}, HTML Length: {len(item['html'])}")

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"out/PRIMARY-{item['url']}-{timestamp}.html"

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(item["html"])

        # Yield the primary item
        yield item

    def parse_secondary(self, response):
        logger.debug(f"Parsing response from secondary URL: {response.url}")
        item = StrippedHtmlItem()
        item["html"] = self.stripTags(response)
        item["url"] = response.url.split("/")[2]

        # Log the scraped secondary URL and HTML length
        logger.debug(f"Secondary URL: {item['url']}, HTML Length: {len(item['html'])}")

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"out/SECONDARY-{item['url']}-{timestamp}.html"

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(item["html"])

        # Yield the secondary item
        yield item
