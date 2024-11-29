import datetime
import logging
import os
import re
from pathlib import Path
import asyncio
import requests
import httpx

import markdownify as md

from app import app
from scraper.items.site_item import SiteItem

logger = logging.getLogger()


class SaveToMdFilePipeline:

    def fetch_description(self, url):
        ai_service_url = os.getenv(
            "AI_SERVICE_URL", "http://ai-description:8000/generate-description/"
        )
        try:
            response = httpx.post(ai_service_url, json={"url": url})
            response.raise_for_status()
            return response.json().get("description", "No description available")
        except Exception as e:
            logger.error(f"Request to {ai_service_url} failed: {e}")
            return f"Error generating description: {e}"

    # Replace ![](image_url) with AI description
    def replace_images_with_descriptions(self, md_text):
        def replacement(match):
            image_url = match.group(2)  # Match the image URL (2nd capture group)
            description = self.fetch_description(image_url)
            logger.debug(f"For image {image_url} generated description: {description}")
            return f"<image: {description}>"

        pattern = r"!\[(.*?)\]\((https?://[^\s]+?\.(?:jpg|jpeg|png))\)"
        updated_text = re.sub(pattern, replacement, md_text)

        return updated_text

    # Remove multiple newlines
    def remove_newlines(self, md_text):
        return re.sub(r"\n\s*\n+", "\n\n", md_text)

    def remove_links(self, md_text):
        pattern = r"\[([^\]]+)\]\((https?://[^\s]+)\)"
        return re.sub(pattern, r"\1", md_text)

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
        md_text = self.replace_images_with_descriptions(md_text)
        md_text = self.remove_newlines(md_text)
        md_text = self.remove_links(md_text)

        with open(Path(output_dir, filename), "w") as f:
            f.write(md_text)

        return item
