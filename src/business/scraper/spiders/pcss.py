import json
import os

import scrapy
from bs4 import BeautifulSoup

from business.scraper.items.stripped_html_item import StrippedHtmlItem
from business.web2ai.html_filter import HtmlFilter
from log_utils import configure_logger

logger = configure_logger()


class PcssSpider(scrapy.Spider):
    name = "pcss"
    custom_settings = {"DEPTH_LIMIT": 1}

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
        yield scrapy.Request(self.primary_url, callback=self.parse_main)

    def parse_main(self, response):
        logger.debug(f"Parsing response from primary URL: {response.url}")
        item = StrippedHtmlItem()
        item["html"] = self.stripTags(response)
        item["url"] = "".join(response.url.split("/")[2:])

        # Log the scraped primary URL and HTML length
        logger.debug(f"Primary URL: {item['url']}, HTML Length: {len(item['html'])}")

        for next_page in response.css("a::attr(href)").extract():
            if (
                next_page is not None
                and next_page
                and next_page.startswith("https://www.pcss.pl/")
            ):
                next_page = response.urljoin(next_page)
                logger.debug(f"Next page: {next_page}")
                yield scrapy.Request(
                    next_page,
                    callback=self.parse_rest,
                    meta={"primary_html": item["html"]},
                )

    def parse_rest(self, response):
        logger.debug(f"Parsing response from secondary URL: {response.url}")
        item = StrippedHtmlItem()
        item["html"] = self.stripTags(response)
        item["url"] = "".join(response.url.split("/")[2:])

        # Log the scraped secondary URL and HTML length
        logger.debug(f"Secondary URL: {item['url']}, HTML Length: {len(item['html'])}")

        item["json"] = json.dumps(
            self.filter_html(response.meta["primary_html"], item["html"])
        )
        # Yield the secondary item
        yield item

    def filter_html(self, primary_html, secondary_html):
        logger.debug("Filtering HTML")

        # Print debug information about primary and secondary data
        logger.debug(f"Primary data available: {self.primary_data is not None}")
        logger.debug(f"Secondary data available: {self.secondary_data is not None}")

        html_filter = HtmlFilter(primary_html, secondary_html)

        return html_filter.filter_output()
