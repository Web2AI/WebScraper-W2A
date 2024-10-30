from bs4 import BeautifulSoup, Comment


class UnneccessaryTagsFilter:
    @staticmethod
    def filter(soup: BeautifulSoup) -> BeautifulSoup:
        """Removes unnecessary tags from the soup."""
        # Remove unnecessary tags
        for tag in soup.find_all(
            ["script", "style", "head", "link", "noscript", "doctype", "nav", "header"]
        ):
            tag.decompose()

        for tag in soup.find_all(
            id=lambda x: x
            and any(
                keyword in x
                for keyword in [
                    "footer",
                    "psnc-posts-section",
                    "psnc-post-news-section",
                ]
            )
        ):
            tag.decompose()

        for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
            comment.extract()

        return soup
