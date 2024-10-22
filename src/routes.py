from flask import Blueprint
from flask import current_app as app
from flask import jsonify, render_template, request

from business.scraper.scrapy_runner import ScrapyRunner

main = Blueprint("main", __name__)

scrapy_runner = ScrapyRunner()


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/scrape", methods=["POST"])
def scrape():
    url = request.form.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        request_id = id(request)

        scrapy_runner.scrape(url, request_id)

        error = scrapy_runner.errors.get(request_id)
        if error:
            return jsonify({"error": error}), 500

        results = scrapy_runner.results.get(request_id)
        return jsonify({"results": results}), 200

    except Exception as e:
        app.logger.exception("An exception occurred during scraping")
        return jsonify({"error": str(e)}), 500
