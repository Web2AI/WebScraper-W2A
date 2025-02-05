import logging
from urllib.parse import unquote

from flask import Blueprint
from flask import current_app as app
from flask import jsonify, render_template, request
from scrapy.utils.serialize import ScrapyJSONEncoder

from models import AttachmentModel, SiteModel, db
from scraper.scrapy_runner import ScrapyRunner

logger = logging.getLogger()

main = Blueprint("main", __name__)

scrapy_runner = ScrapyRunner()


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/recreate_db")
def recreate_db():
    db.drop_all()
    db.create_all()
    app.chromadb_client.reset()
    sites = SiteModel.query.all()
    message = "Database has been recreated successfully!"
    return render_template("history.html", sites=sites, message=message)


@main.route("/history")
def history():
    sites = SiteModel.query.all()
    return render_template("history.html", sites=sites)


@main.route("/scrape", methods=["POST"])
def scrape():
    primary_url = request.json.get("primary_url")
    use_image_descriptor = request.json.get("use_image_descriptor")
    depth_limit = request.json.get("depth_limit")
    if not primary_url:
        return jsonify({"error": "URL is required"}), 400

    try:
        request_id = id(request)

        scrapy_runner.scrape(primary_url, use_image_descriptor, depth_limit, request_id)

        error = scrapy_runner.errors.get(request_id)
        if error:
            return jsonify({"error": error}), 500

        results = scrapy_runner.results.get(request_id)
        return ScrapyJSONEncoder().encode({"results": results}), 200

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
    attachments = AttachmentModel.query.filter_by(site_url=decoded_url).all()
    page_item = SiteModel.query.get(decoded_url)

    return render_template(
        "attachment.html",
        url=decoded_url,
        attachments=attachments,
        page_item=page_item,
    )


@main.route("/jobs")
def jobs():
    return render_template(
        "jobs.html",
    )
