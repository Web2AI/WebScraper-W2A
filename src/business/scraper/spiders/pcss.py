import scrapy
from bs4 import BeautifulSoup

from business.scraper.items.stripped_html_item import StrippedHtmlItem


class PcssSpider(scrapy.Spider):
    name = "pcss"

    def __init__(
        self, url, request_id, **kwargs
    ):  # The category variable will have the input URL.
        self.url = url
        self.request_id = request_id
        print(self.request_id)
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
            # Remove elements with id containing "nav"
        for tag in soup.find_all(id=lambda x: x and "nav" in x):
            tag.decompose()
        for tag in soup.find_all(className=lambda x: x and "nav" in x):
            tag.decompose()

        # Save the cleaned HTML
        return soup.prettify(encoding="utf-8")

    def start_requests(self):
        request = scrapy.Request(self.url, callback=self.parse)

        yield request

    def parse(self, response):
        item = StrippedHtmlItem()
        item["html"] = self.stripTags(response).decode()
        item["url"] = response.url.split("/")[-2]

        yield item
