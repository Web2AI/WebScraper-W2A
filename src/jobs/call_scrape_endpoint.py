import logging
import requests

from constants import TIMEOUT

logger = logging.getLogger()


def call_scrape_endpoint(primary_url):
    try:
        # TODO remove hardcoded base url
        response = requests.post(
            "http://127.0.0.1:5000/scrape",
            json={"primary_url": primary_url},
            timeout=TIMEOUT,
        )
        if response.status_code == 200:
            logger.info(f"Scraping for {primary_url} triggered successfully!")
        else:
            logger.error("Failed to trigger job:", response.status_code)
    except Exception as e:
        logger.error("Error triggering job:", e)
