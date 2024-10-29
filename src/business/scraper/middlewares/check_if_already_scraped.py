from scrapy.exceptions import IgnoreRequest

from app import app
from log_utils import configure_logger
from models import Site

logger = configure_logger()


class CheckIfAlreadyScrapedDownloaderMiddleware:
    def process_request(self, request, spider):
        with app.app_context():
            if (
                len(Site.query.filter_by(url="".join(request.url.split("/")[2:])).all())
                > 0
            ):
                logger.info(f"Already scraped {request.url}, skipping")
                raise IgnoreRequest
        return None
