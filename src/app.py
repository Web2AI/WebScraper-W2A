import logging

import crochet
from flask import Flask, jsonify, render_template, request
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from scrapy.signalmanager import dispatcher

from business.web2ai.spiders.pcss import PcssSpider

# Initialize crochet
crochet.setup()

# Initialize Flask
app = Flask(__name__)

# Configure logging for both Scrapy and Flask
logging.basicConfig(
    level=logging.DEBUG,  # Set log level to DEBUG
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

# Ensure Flask uses the logger at DEBUG level
app.logger.setLevel(logging.DEBUG)

# Store results and errors per request
request_results: dict[int, list] = {}
request_errors = {}


# Scrapy signal handler for when the spider closes
def _spider_closing(spider: PcssSpider, reason):
    request_id = spider.request_id
    app.logger.debug(f"Spider closed: {reason} for request {request_id}")


# Append the data to the output data list.
def _crawler_result(item, response, spider: PcssSpider):
    request_results[spider.request_id].append(dict(item))
    app.logger.debug(f"Item scraped for request {spider.request_id}")


# By default Flask will come into this when we run the file
@app.route("/")
def index():
    return render_template("index.html")


# Wait for the spider to complete before returning the response
@app.route("/scrape", methods=["POST"])
def scrape():
    primary_url = request.form.get("primary_url")
    secondary_url = request.form.get("secondary_url")

    if not primary_url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Use a unique ID (request context ID) to store results for each user request
        request_id = id(request)
        app.logger.debug(f"Starting scrape for request {request_id}")

        # Initialize the result storage for this request
        request_results[request_id] = []
        request_errors[request_id] = None

        # Run the spider and wait for it to finish
        result = scrape_with_crochet(primary_url, secondary_url, request_id)

        # If an error occurred, return it in the response
        if request_errors[request_id]:
            return jsonify({"error": request_errors[request_id]}), 500

        # Return the result for this specific request
        return jsonify({"results": request_results[request_id]}), 200

    except Exception as e:
        app.logger.exception("Exception occurred during scraping")
        return jsonify({"error": str(e)}), 500


@crochet.wait_for(timeout=60.0)  # Wait for the result (adjust timeout as necessary)
def scrape_with_crochet(primary_url, secondary_url, request_id):
    global request_results, request_errors

    settings = Settings()
    # settings.set(
    #     "ITEM_PIPELINES",
    #     {
    #         "business.web2ai.pipelines.SaveToHtmlFilePipeline": 300,
    #     },
    # )
    settings.set("LOG_LEVEL", "DEBUG")

    # Setting up Scrapy Crawler
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    dispatcher.connect(_spider_closing, signal=signals.spider_closed)
    runner = CrawlerRunner(settings)

    # Run the spider and wait for it to complete
    deferred = runner.crawl(
        PcssSpider,
        primary_url=primary_url,
        secondary_url=secondary_url,
        request_id=request_id,
    )
    deferred.addErrback(handle_error, request_id)

    return deferred


def handle_error(failure, request_id):
    global request_errors
    request_errors[request_id] = str(failure)
    app.logger.error(f"Error occurred for request {request_id}: {failure}")


if __name__ == "__main__":
    app.run(debug=True)  # nosec
