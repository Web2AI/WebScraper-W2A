import datetime
import logging
import os

import scrapy
from bs4 import BeautifulSoup

from business.web2ai.html_filter import HtmlFilter
from business.web2ai.items import StrippedHtmlItem
from logger_setup import configure_logger

logger = configure_logger()

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

    def parse_primary(self, response):
        logger.debug(f"Parsing response from primary URL: {response.url}")
        item = StrippedHtmlItem()
        item["html"] = self.stripTags(response)
        item["url"] = "".join(response.url.split("/")[2:])

        # Log the scraped primary URL and HTML length
        logger.debug(f"Primary URL: {item['url']}, HTML Length: {len(item['html'])}")

        self.primary_data = item["html"]
        self.filter_html()
        # Yield the primary item
        yield item

    def parse_secondary(self, response):
        logger.debug(f"Parsing response from secondary URL: {response.url}")
        item = StrippedHtmlItem()
        item["html"] = self.stripTags(response)
        item["url"] = "".join(response.url.split("/")[2:])

        # Log the scraped secondary URL and HTML length
        logger.debug(f"Secondary URL: {item['url']}, HTML Length: {len(item['html'])}")

        self.secondary_data = item["html"]
        self.filter_html()
        # Yield the secondary item
        yield item

    def filter_html(self):
        print("Filtering HTML")

        # Print debug information about primary and secondary data
        logger.debug(f"Primary data available: {self.primary_data is not None}")
        logger.debug(f"Secondary data available: {self.secondary_data is not None}")

        if self.primary_data is not None and self.secondary_data is not None:

            output_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../../out")
            )

            html_filter = HtmlFilter(
                self.primary_data, self.secondary_data, output_dir=output_dir
            )

            html_filter.filter_output()
