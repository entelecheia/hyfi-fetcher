import logging
from typing import List, Optional

from .base import BaseFetcher

logger = logging.getLogger(__name__)


class SierraClubFetcher(BaseFetcher):
    """
    Fetcher for Sierra Club website.
    """

    _config_name_: str = "sierraclub"
    _config_group_: str = "/fetcher"
    output_dir: str = f"workspace/datasets{_config_group_}/{_config_name_}"

    base_url: str = "https://www.sierraclub.org"
    search_url: str = base_url + "/press-releases?_wrapper_format=html&page={page}"
    search_keywords: List[str] = []
    use_playwright: bool = False

    link_find_all_name: str = "div"
    link_find_all_attrs: dict = {"class": "post"}
    lint_article_name: str = "h3"
    lint_article_attrs: dict = {"class": "post-title"}

    def _parse_page_links(
        self,
        page_url: str,
        print_every: int = 10,
        verbose: bool = False,
    ) -> Optional[List[dict]]:
        """Get the links from the given page."""
        links = []
        soup = self.get_soup(page_url)

        # Find all articles
        articles = soup.find_all(
            self.link_find_all_name, attrs=self.link_find_all_attrs
        )

        for article_no, article in enumerate(articles):
            # Extract and print article information
            title_div = article.find(
                self.lint_article_name, attrs=self.lint_article_attrs
            )
            if title_div is None:
                logger.info("No title found for article %s", article_no)
                continue
            title = title_div.text
            url = self.base_url + article.find("a")["href"]

            date_ = article.find("div", class_="views-field-field-published-date").find(
                "div", class_="field-content"
            )
            item_date = date_.text.strip() if date_ else ""

            if verbose and article_no % print_every == 0:
                logger.info("Title: %s", title)
                logger.info("URL: %s", url)
            link = {
                "title": title,
                "timestamp": item_date,
                "url": url,
            }
            links.append(link)
        return links

    def _parse_article_text(self, url: str) -> Optional[dict]:
        """Parse the article text from the given divs."""
        soup = self.get_soup(url)
        if soup is None:
            return None

        title = soup.find("h1", class_="page-header").text.strip()
        content = soup.find("article", class_="press-release").text.strip()
        return {
            "title": title,
            "content": content,
        }
