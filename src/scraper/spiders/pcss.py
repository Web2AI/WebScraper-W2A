import hashlib
import json
import logging
import re
from urllib.parse import urlparse

import scrapy
from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor

from constants import TIMEOUT
from scraper.filters.common_tags_filter import CommonTagsFilter
from scraper.filters.unneccessary_tags_filter import UnneccessaryTagsFilter
from scraper.items.attachment_item import AttachmentItem
from scraper.items.site_item import SiteItem

logger = logging.getLogger()


class PcssSpider(scrapy.Spider):
    # TODO: when changing subdomain use different common_tags_filter (maybe dict of them?)
    allowed_domains = [  # all pcss.pl and pionier.net.pl subdomains
        "pcss.pl",
        "pionier.net.pl",
        "host.docker.internal",
    ]
    denied_links = r"\.(zip|exe|rar|tar|gz|7z|docx|mp3|mp4|xml)$"
    downloadable_extensions = r"\.(pdf|doc|docx)$"
    name = "pcss"
    download_timeout = TIMEOUT

    def __init__(self, primary_url, request_id, depth_limit, **kwargs):
        super().__init__(**kwargs)
        self._primary_url = primary_url
        self.request_id = request_id
        self.common_tags_filter = None
        self.depth_limit = depth_limit
        logger.debug(f"Spider initialized with request_id: {self.request_id}")

    def start_requests(self):
        logger.debug(f"Starting request for primary URL: {self._primary_url}")
        yield scrapy.Request(self._primary_url, callback=self.parse)

    def parse(self, response):
        # Filter out denied links
        if re.search(self.denied_links, response.url):
            logger.warning(f"Denied link found, skipping: {response.url}")
            return

        # Save to database if it's a downloadable file
        # In this case, the attachment's url is the parent's url
        if re.search(self.downloadable_extensions, response.url):
            logger.debug(f"Saving to database file: {response.url}")
            yield AttachmentItem(
                site_item=response.meta.get("parent_item"),
                type=response.url.split(".")[-1],
                content=None,
                url=response.url,
            )
            return

        try:
            site = self.create_site_item(response, response.meta.get("parent_item"))
        except ValueError as e:
            logger.error(f"Error while parsing the {response.url} : {e}")
            return  # skip this site

        yield site

        if response.meta["depth"] < self.depth_limit:
            for next_page in LinkExtractor().extract_links(response):
                yield response.follow(
                    next_page,
                    callback=self.parse,
                    meta={"parent_item": site},
                )

        yield from self.extract_attachments(site)

    def create_site_item(self, response, parent_item=None):
        soup = BeautifulSoup(response.body, "html.parser")
        item = SiteItem()
        item["html"] = UnneccessaryTagsFilter.filter(soup).html.prettify()
        item["url"] = self.remove_protocol(response.url)

        if parent_item:
            item["json"] = self.common_tags_filter.filter(item["html"])
        else:
            self.common_tags_filter = CommonTagsFilter(item["html"])
            item["json"] = self.common_tags_filter.get_context()

        item["page_hash"] = self.generate_sha256_hash(item["json"])
        if parent_item:
            item["parent_item"] = parent_item

        logger.debug(f"Primary URL: {item['url']}, HTML Length: {len(item['html'])}\n")
        return item

    def remove_protocol(self, url):
        return urlparse(url).netloc + urlparse(url).path

    def generate_sha256_hash(self, content):
        sha256 = hashlib.sha256()
        content = json.dumps(content, ensure_ascii=False)
        sha256.update(content.encode())
        return sha256.hexdigest()

    def extract_attachments(self, site_item):
        """Extract images, videos, and other attachments from the page."""
        soup = BeautifulSoup(site_item["html"], "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                yield AttachmentItem(
                    site_item=site_item,
                    type="image",
                    content=None,
                    url=src,
                )
