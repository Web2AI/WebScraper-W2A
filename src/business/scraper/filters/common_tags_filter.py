from bs4 import BeautifulSoup, Tag

from log_utils import configure_logger

logger = configure_logger()


class CommonTagsFilter:
    def __init__(self, context_html):
        context_soup = BeautifulSoup(context_html, "html.parser")
        context_texts = context_soup.find_all(text=True)
        context_texts = [text.strip() for text in context_texts if text.strip() != ""]
        self.context = set(context_texts)

    def filter(self, scraped_html):
        """Removes the common parts of the tag based on the context, preserving the order of unique texts."""
        soup1 = BeautifulSoup(scraped_html, "html.parser")
        # Extract all text nodes from the tag and clean them
        tag_texts = soup1.find_all(text=True)
        tag_texts = [text.strip() for text in tag_texts if text.strip() != ""]

        # Collect unique texts while preserving the order
        unique_texts = [text for text in tag_texts if text not in self.context]
        return unique_texts
