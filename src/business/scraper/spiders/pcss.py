import json
from urllib.parse import urlparse

import scrapy
from bs4 import BeautifulSoup

from business.scraper.filters.common_tags_filter import CommonTagsFilter
from business.scraper.filters.unneccessary_tags_filter import UnneccessaryTagsFilter
from business.scraper.items.stripped_html_item import StrippedHtmlItem
from log_utils import configure_logger

logger = configure_logger()


class PcssSpider(scrapy.Spider):
    name = "pcss"
    custom_settings = {"CLOSESPIDER_TIMEOUT": 15, "DEPTH_LIMIT": 1}
    common_tags_filter = None

    def __init__(self, primary_url, request_id, **kwargs):
        self._primary_url = primary_url
        self.request_id = request_id
        logger.debug(f"Spider initialized with request_id: {self.request_id}")
        super().__init__(**kwargs)

    def get_next_pages(self, response):
        for next_page in response.css("a::attr(href)").extract():
            if (
                next_page is not None
                and next_page
                and next_page.startswith(
                    "https://www.pcss.pl/"
                )  # TODO: only links with given domain name
            ):
                next_page = response.urljoin(next_page)
                yield next_page

    def remove_protocol(self, url):
        parsed_url = urlparse(url)
        return parsed_url.netloc + parsed_url.path

    def start_requests(self):
        logger.debug(f"Starting request for primary URL: {self._primary_url}")
        yield scrapy.Request(self._primary_url, callback=self.parse_main)

    def parse_main(self, response):
        # TODO: Right now main page doesn't filter out
        #       we don't yield item (because of no secondary page for filtering)
        logger.debug(f"Parsing response from primary URL: {response.url}")
        item = StrippedHtmlItem()
        soup = BeautifulSoup(response.body, "html.parser")
        # TODO: maybe we should move this to a seperate function too...
        item["html"] = UnneccessaryTagsFilter.filter(soup).html.prettify()
        item["url"] = self.remove_protocol(response.url)
        self.common_tags_filter = CommonTagsFilter(item["html"])

        # Log the scraped primary URL and HTML length
        logger.debug(f"Primary URL: {item['url']}, HTML Length: {len(item['html'])}")

        for next_page in self.get_next_pages(response):
            logger.debug(f"Next page: {next_page}")
            yield scrapy.Request(
                next_page,
                callback=self.parse_rest,
                meta={"parent_html": item["html"], "parent_url": item["url"]},
            )

        # TODO: yield primary item (not filtered and no json)

    def parse_rest(self, response):
        logger.debug(f"Parsing response from secondary URL: {response.url}")
        item = StrippedHtmlItem()
        soup = BeautifulSoup(response.body, "html.parser")
        item["html"] = UnneccessaryTagsFilter.filter(soup).html.prettify()
        item["url"] = self.remove_protocol(response.url)
        item["parent_url"] = response.meta["parent_url"]

        # Log the scraped secondary URL and HTML length
        logger.debug(f"Secondary URL: {item['url']}, HTML Length: {len(item['html'])}")

        item["json"] = json.dumps(self.common_tags_filter.filter(item["html"]))
        yield item  # TODO: add yield scrapy request like in parse_main (and adjust depth_limit)
