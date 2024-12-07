from functools import cached_property

import crochet
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from scrapy.signalmanager import dispatcher

from constants import TIMEOUT
from scraper.spiders.pcss import PcssSpider

crochet.setup()  # Initialize crochet


class ScrapyRunner:
    def __init__(self):
        self.results = {}
        self.errors = {}

    def _spider_closing(self, spider, reason):
        pass  # cleanup logic if needed

    def _crawler_result(self, item, response, spider: PcssSpider):
        self.results[spider.request_id].append(dict(item))

    @cached_property
    def _settings(self):
        settings = Settings()
        settings.set(
            "ITEM_PIPELINES",
            {
                # "scraper.pipelines.save_to_html_file_pipeline.SaveToHtmlFilePipeline": 300, # Obsolete
                "scraper.pipelines.save_to_pdf_pipeline.SaveToPdfPipeline": 333,
                "scraper.pipelines.save_to_db_pipeline.SaveToDBPipeline": 350,
            },
        )
        # settings.set("CONCURRENT_REQUESTS", 32)
        # settings.set("CONCURRENT_REQUESTS_PER_DOMAIN", 16)
        # settings.set("CONCURRENT_REQUESTS_PER_IP", 16)
        settings.set("LOG_LEVEL", "DEBUG")

        return settings

    @cached_property
    def _runner(self):
        dispatcher.connect(self._crawler_result, signal=signals.item_scraped)
        dispatcher.connect(self._spider_closing, signal=signals.spider_closed)
        return CrawlerRunner(self._settings)

    def _handle_error(self, failure, request_id):
        self.errors[request_id] = str(failure)

    @crochet.wait_for(timeout=TIMEOUT)
    def scrape(self, primary_url, use_image_descriptor, request_id):
        # Initialize result storage for this request
        self.results[request_id] = []
        self.errors[request_id] = None

        # Run the spider and handle errors
        deferred = self._runner.crawl(
            PcssSpider,
            primary_url=primary_url,
            request_id=request_id,
            use_image_descriptor=use_image_descriptor,
        )
        deferred.addErrback(self._handle_error, request_id)

        return deferred
