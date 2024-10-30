from bs4 import BeautifulSoup, Tag

from business.scraper.filters.unneccessary_tags_filter import \
    UnneccessaryTagsFilter
from log_utils import configure_logger

logger = configure_logger()


class CommonTagsFilter:
    def __init__(self):
        # TODO: maybe we should consider changing functions to staticmethods...
        pass

    def _get_attributes(self, tag):
        """Returns a dictionary of attributes for a tag excluding the 'name' attribute."""
        return {
            key: value
            for key, value in getattr(tag, "attrs", {}).items()
            if key != "name"
        }

    def _create_common_structure(self, tag1, tag2, soup=None):
        """Recursively compares two tags and returns their common structure as a new tag."""

        # Initialize a BeautifulSoup object if not provided (for recursion)
        if soup is None:
            soup = BeautifulSoup("", "html.parser")

        # If either tag is not a valid tag or their names differ, return None
        if (
            not isinstance(tag1, Tag)
            or not isinstance(tag2, Tag)
            or tag1.name != tag2.name
        ):
            return None

        # Create a new tag based on the common attributes
        attrs1 = getattr(tag1, "attrs", {})
        attrs2 = getattr(tag2, "attrs", {})
        if attrs1 == attrs2:
            new_tag = soup.new_tag(tag1.name, self._get_attributes(tag1))
        else:
            new_tag = soup.new_tag(tag1.name)

        # If both tags have the same text content, add it to the new tag
        if tag1.string == tag2.string and tag1.string is not None:
            new_tag.string = tag1.string

        # Recursively compare children
        last_match = 0
        for child1 in tag1.children:
            children2 = list(tag2.children)  # Convert to list to allow indexing
            for child2 in children2[last_match:]:
                common_child = self._create_common_structure(child1, child2, soup)
                if common_child:
                    last_match = children2.index(child2) + 1
                    new_tag.append(common_child)
                    break  # Stop once a common child is found

        return new_tag

    def _remove_common_parts(self, tag, common_structure):
        """Removes the common parts of the tag based on the common structure, preserving the order of unique texts."""

        # Extract all text nodes from the common structure and clean them
        common_texts = common_structure.find_all(text=True)
        common_texts = [text.strip() for text in common_texts if text.strip() != ""]
        common_texts = set(common_texts)  # Use a set for faster lookup

        # Extract all text nodes from the tag and clean them
        tag_texts = tag.find_all(text=True)
        tag_texts = [text.strip() for text in tag_texts if text.strip() != ""]

        # Collect unique texts while preserving the order
        unique_texts = [text for text in tag_texts if text not in common_texts]

        return unique_texts

    def filter(self, scraped_html, context_html):

        soup1 = BeautifulSoup(scraped_html, "html.parser")
        soup2 = BeautifulSoup(context_html, "html.parser")

        soup1 = UnneccessaryTagsFilter.filter(soup1)
        soup2 = UnneccessaryTagsFilter.filter(soup2)

        common_structure = self._create_common_structure(soup1, soup2)

        return self._remove_common_parts(soup1, common_structure)
