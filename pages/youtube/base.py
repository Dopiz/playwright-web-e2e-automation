from playwright.sync_api import Page

from pages.base import BasePage
from pages.youtube.search_bar import SearchBarComponent


class YouTubeBasePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._youtube_config = self._config.get("youtube")
        self.search_bar = SearchBarComponent(self.page)

    def open(self):
        self.page.goto(
            self._youtube_config["entry_url"],
            wait_until="domcontentloaded",
        )
