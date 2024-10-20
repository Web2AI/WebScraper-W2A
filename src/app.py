# Description: This file is the main file for the server. It will handle all the requests and responses from the client.
import crochet
from flask import Flask, jsonify, render_template, request
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from scrapy.signalmanager import dispatcher

from business.web2ai.spiders.pcss import PcssSpider

crochet.setup()  # Initialize crochet

app = Flask(__name__)

# Store results and errors per request
request_results: dict[int, list] = {}
request_errors = {}


# Scrapy signal handler for when the spider closes
def _spider_closing(spider: PcssSpider, reason):
    pass # cleanup


# This will append the data to the output data list.
def _crawler_result(item, response, spider: PcssSpider):
    request_results[spider.request_id].append(dict(item))
    app.logger.debug(spider.request_id)


# By Deafult Flask will come into this when we run the file
@app.route("/")
def index():
    return render_template("index.html")


# Wait for the spider to complete before returning the response
@app.route("/scrape", methods=["POST"])
def scrape():
    url = request.form.get("url")  # Get the URL from query parameter

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Use a unique ID (request context ID) to store results for each user request
        request_id = id(request)
        app.logger.debug(request_id)

        # Initialize the result storage for this request
        request_results[request_id] = []
        request_errors[request_id] = None

        # Run the spider and wait for it to finish
        result = scrape_with_crochet(url, request_id)

        # If an error occurred, return it in the response
        if request_errors[request_id]:
            return jsonify({"error": request_errors[request_id]}), 500

        # Return the result for this specific request
        return jsonify({"results": request_results[request_id]}), 200

    except Exception as e:
        app.logger.exception("")
        return jsonify({"error": str(e)}), 500


@crochet.wait_for(timeout=60.0)  # Wait for the result (adjust timeout as necessary)
def scrape_with_crochet(url, request_id):
    global request_results, request_errors

    settings = Settings()
    settings.set(
        "ITEM_PIPELINES",
        {
            "business.web2ai.pipelines.SaveToHtmlFilePipeline": 300,
        },
    )
    settings.set("LOG_LEVEL", "DEBUG")

    # Setting up Scrapy Crawler
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    dispatcher.connect(_spider_closing, signal=signals.spider_closed)
    runner = CrawlerRunner(settings)

    # Run the spider and wait for it to complete
    deferred = runner.crawl(PcssSpider, url=url, request_id=request_id)
    deferred.addErrback(handle_error, request_id)

    return deferred


def handle_error(failure, request_id):
    global request_errors
    request_errors[request_id] = str(failure)


if __name__ == "__main__":
    app.run(debug=True)  # nosec
