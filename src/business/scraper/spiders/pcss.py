import datetime
import hashlib
import json
from urllib.parse import urlparse

import scrapy
from bs4 import BeautifulSoup

from business.scraper.filters.common_tags_filter import CommonTagsFilter
from business.scraper.filters.unneccessary_tags_filter import UnneccessaryTagsFilter
from business.scraper.items.attachment_item import AttachmentItem
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

        # for next_page in self.get_next_pages(response):
        #     logger.debug(f"Next page: {next_page}")
        #     yield scrapy.Request(
        #         next_page,
        #         callback=self.parse_rest,
        #         meta={"parent_html": item["html"], "parent_url": item["url"]},
        #     )
        #     break
        filtered_content = self.common_tags_filter.filter(item["html"])
        item["parent_url"] = item["url"]
        item["json"] = json.dumps(filtered_content)
        item["page_hash"] = self.generate_sha256_hash(item["json"])
        logger.info(f"Page hash: {item['page_hash']}")
        yield item

    def parse_rest(self, response):
        logger.debug(f"Parsing response from secondary URL: {response.url}")
        item = StrippedHtmlItem()
        soup = BeautifulSoup(response.body, "html.parser")
        filtered_soup = UnneccessaryTagsFilter.filter(soup)
        item["html"] = filtered_soup.prettify()
        item["url"] = self.remove_protocol(response.url)
        item["parent_url"] = response.meta["parent_url"]

        # Log the scraped secondary URL and HTML length
        logger.debug(f"Secondary URL: {item['url']}, HTML Length: {len(item['html'])}")
        filtered_content = self.common_tags_filter.filter(item["html"])
        item["json"] = json.dumps(filtered_content)
        item["page_hash"] = self.generate_sha256_hash(item["json"])
        logger.info(f"Page hash: {item['page_hash']}")
        yield item  # TODO: add yield scrapy request like in parse_main (and adjust depth_limit)

        # Extract and yield attachments
        # THE ATTACHMENTS SHOULD BE EXTRACTED AFTER FILTERING!!!
        yield from self.extract_attachments(item["url"], filtered_soup)

    def generate_sha256_hash(self, content):
        sha256 = hashlib.sha256()
        sha256.update(content.encode())
        return sha256.hexdigest()

    def extract_attachments(self, site_url, soup):
        """Extract images, videos, and other attachments from the page."""

        logger.debug(f"Extracting attachments from {site_url}")

        # Extract images
        images = soup.find_all("img")
        for img in images:
            src = img.get("src")
            if src:
                attachment = AttachmentItem()
                attachment["site_url"] = site_url
                attachment["type"] = "image"
                attachment["content"] = None
                attachment["url"] = src

                logger.debug("Yielding image attachment")
                yield attachment
