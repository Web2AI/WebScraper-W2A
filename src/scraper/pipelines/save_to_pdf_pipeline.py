import asyncio
import datetime
import logging
import os
import re
from pathlib import Path

import httpx
import markdown2
import markdownify as md
import requests
from weasyprint import HTML

from app import app
from scraper.items.site_item import SiteItem

logger = logging.getLogger()


class SaveToPdfPipeline:

    def fetch_description(self, url):
        ai_service_url = os.getenv(
            "AI_SERVICE_URL", "http://ai-description:8000/generate-description/"
        )
        try:
            url = re.findall(r"https?://[^\s]+?\.(?:jpg|jpeg|png|gif|svg)", url)[0]
            response = httpx.post(ai_service_url, json={"url": url}, timeout=10)
            response.raise_for_status()
            return response.json().get("description", "No description available")
        except Exception as e:
            logger.error(f"Request to {ai_service_url} failed: {e}")
            return f"Error generating description: {e} url: {url}"

    # Replace ![](image_url) with AI description
    def replace_images_with_descriptions(self, md_text):
        pattern = (
            r"!\[(.*?)\]\((https?://[^\s]+?\.(?:jpg|jpeg|png|gif))(?:\s+\".*?\")?\)"
        )
        matches = re.findall(pattern, md_text)
        logger.debug(f"Found {len(matches)} image(s) in the Markdown text")
        # tasks = {
        #     image_url: self.fetch_description(image_url)
        #     for alt_text, image_url in matches
        #     if not alt_text
        # }
        # results = await asyncio.gather(*tasks)
        for alt_text, image_url in matches:
            description = alt_text if alt_text else self.fetch_description(image_url)
            # description = alt_text if alt_text else results[image_url]
            logger.debug(f"Generated description for {image_url}: {description}")
            replacement_pattern = rf"!\[{alt_text}\]\({image_url}(?:\s+\".*?\")?\)"
            replacement = f"*image: {description}*"
            md_text = re.sub(replacement_pattern, replacement, md_text, count=1)

        return md_text

    # Remove multiple newlines
    def remove_newlines(self, md_text):
        return re.sub(r"\n\s*\n+", "\n\n", md_text)

    def remove_svg(self, md_text):
        patern = r"!\[(.*?)\]\((https?://[^\s]+?\.(?:svg))(?:\s+\".*?\")?\)"
        return re.sub(patern, "*image: svg*", md_text)

    def process_item(self, item, spider):
        if not isinstance(item, SiteItem):
            return item

        with app.app_context():
            if not item.should_save:
                return item

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        project_dir = os.getenv("PROJECT_DIR")
        output_dir = Path(project_dir, "out").resolve()
        filename = f"{item.get('url').replace('/','')}-{timestamp}"

        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        md_text = md.markdownify(item.get("html"), heading_style="ATX")
        md_text = self.replace_images_with_descriptions(md_text)
        md_text = self.remove_newlines(md_text)
        md_text = self.remove_svg(md_text)

        html_text = markdown2.markdown(md_text)
        HTML(string=html_text).write_pdf(Path(output_dir, f"{filename}.pdf"))

        # with open(Path(output_dir, f"{filename}.md"), "w") as f:
        #     f.write(md_text)

        return item
