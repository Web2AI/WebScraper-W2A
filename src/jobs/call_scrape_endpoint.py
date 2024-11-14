import requests

from constants import TIMEOUT


def call_scrape_endpoint(primary_url):
    try:
        # TODO remove hardcoded base url
        response = requests.post(
            "http://127.0.0.1:5000/scrape",
            json={"primary_url": primary_url},
            timeout=TIMEOUT,
        )
        if response.status_code == 200:
            print("Job triggered successfully!")
        else:
            print("Failed to trigger job:", response.status_code)
    except Exception as e:
        print("Error triggering job:", e)
