import logging
from typing import List, Optional

from bs4 import BeautifulSoup

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
        try:
            response = self.request(page_url, use_playwright=True)
            # Check if page exists (status code 200) or not (status code 404)
            if response.status_code == 404:
                logger.info("Page [%s] does not exist, stopping...", page_url)
                return None
            soup = BeautifulSoup(response.text, "html.parser")

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

                date_ = article.find(
                    "div", class_="views-field-field-published-date"
                ).find("div", class_="field-content")
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
        except Exception as e:
            logger.error("Error while fetching the page url: %s", page_url)
            logger.error(e)
        return links

    def _parse_article_text(self, url: str) -> Optional[dict]:
        """Parse the article text from the given divs."""
        try:
            response = self.request(url)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find("h1", class_="page-header").text.strip()
            content = soup.find("article", class_="press-release").text.strip()

            return {
                "title": title,
                "content": content,
            }

        except Exception as e:
            logger.error("Error while scraping the article url: %s", url)
            logger.error(e)
        return None
