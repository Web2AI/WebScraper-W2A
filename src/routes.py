from urllib.parse import unquote

from flask import Blueprint
from flask import current_app as app
from flask import jsonify, render_template, request

from business.scraper.scrapy_runner import ScrapyRunner
from log_utils import configure_logger
from models import Attachment, Site

logger = configure_logger()

main = Blueprint("main", __name__)

scrapy_runner = ScrapyRunner()


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/history")
def history():
    sites = Site.query.all()
    return render_template("history.html", sites=sites)


@main.route("/scrape", methods=["POST"])
def scrape():
    primary_url = request.json.get("primary_url")

    if not primary_url:
        return jsonify({"error": "URL is required"}), 400

    try:
        request_id = id(request)

        scrapy_runner.scrape(primary_url, request_id)

        error = scrapy_runner.errors.get(request_id)
        if error:
            return jsonify({"error": error}), 500

        results = scrapy_runner.results.get(request_id)
        return jsonify({"results": results}), 200

    except Exception as e:
        logger.exception("An exception occurred during scraping")
        return jsonify({"error": str(e)}), 500


@main.route("/attachment")
def attachment():

    # Get the url
    url = request.args.get("url")
    if not url:
        return "URL parameter is missing.", 400

    # Decode the URL if necessary
    decoded_url = unquote(url)

    # Get attachments for the given URL from the database
    attachments = Attachment.query.filter_by(site_url=decoded_url).all()

    return render_template("attachment.html", url=decoded_url, attachments=attachments)
