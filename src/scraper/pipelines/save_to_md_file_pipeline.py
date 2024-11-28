import datetime
import logging
import os
import re
from pathlib import Path
import asyncio
import requests

import markdownify as md

from app import app
from scraper.items.site_item import SiteItem

logger = logging.getLogger()


class SaveToMdFilePipeline:

    async def fetch_description(self, url):
        ai_service_url = os.getenv(
            "AI_SERVICE_URL", "http://ai-description:8000/generate-description/"
        )
        try:
            logger.debug(f"Sending POST request to {ai_service_url} with URL: {url}")
            response = requests.post(ai_service_url, json={"url": url})
            response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx, 5xx)

            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response body: {response.text}")

            return response.json().get("description", "No description available")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return f"Error generating description: {e}"

    # Replace ![](image_url) with AI description
    async def replace_images_with_descriptions(self, md_text):
        def replacement(match):
            image_url = match.group(1)
            description = asyncio.run(self.fetch_description(image_url))
            return f"[image]({description})"

        return re.sub(r"!\[(.*?)\]\((https?://[^\s]+)\)", replacement, md_text)

    # Remove multiple newlines
    def remove_newlines(self, md_text):
        return re.sub(r"\n\s*\n+", "\n\n", md_text)

    async def process_item(self, item, spider):
        if not isinstance(item, SiteItem):
            return item

        with app.app_context():
            if not item.should_save:
                return item

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        project_dir = os.getenv("PROJECT_DIR")
        output_dir = Path(project_dir, "out", "md_files").resolve()
        filename = f"{item.get('url').replace('/','')}-{timestamp}.md"

        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        md_text = md.markdownify(item.get("html"), heading_style="ATX")
        md_text = await self.replace_images_with_descriptions(md_text)
        md_text = self.remove_newlines(md_text)

        with open(Path(output_dir, filename), "w") as f:
            f.write(md_text)

        return item
