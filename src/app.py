# Description: This file is the main file for the server. It will handle all the requests and responses from the client.
# from waitress import serve
import crochet

crochet.setup()

from flask import Flask, render_template, jsonify, request, redirect, url_for
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
import time
import os

# Importing our Scraping Function from the file

from business.web2ai.spiders.pcss import PcssSpider

app = Flask(__name__)

output_data = []
crawl_runner = CrawlerRunner()


# By Deafult Flask will come into this when we run the file
@app.route("/")
def index():
    return render_template("index.html")


# After clicking the Submit Button FLASK will come into this
@app.route("/", methods=["POST"])
def submit():
    if request.method == "POST":
        s = request.form["url"]
        global baseURL
        baseURL = s

        return redirect(url_for("scrape"))  # Passing to the Scrape function


@app.route("/scrape")
def scrape():

    scrape_with_crochet(baseURL=baseURL)  # Passing that URL to our Scraping Function

    time.sleep(20)  # Pause the function while the scrapy spider is running

    return "GIT"


@crochet.run_in_reactor
def scrape_with_crochet(baseURL):
    # This will connect to the dispatcher that will kind of loop the code between these two functions.
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)

    # This will connect to the ReviewspiderSpider function in our scrapy file and after each yield will pass to the crawler_result function.
    eventual = crawl_runner.crawl(PcssSpider, url=baseURL)
    return eventual


# This will append the data to the output data list.
def _crawler_result(item, response, spider):
    output_data.append(dict(item))


if __name__ == "__main__":
    app.run(debug=True)
