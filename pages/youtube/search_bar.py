from playwright.sync_api import Page, TimeoutError

from pages.base import BasePage, step


class SearchBarComponent(BasePage):
    element_file_path = "youtube/search_bar"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @step("Click search button narrow if visible")
    def click_search_button_narrow_if_visible(self, timeout: int = 3_000):
        try:
            self.locator("SEARCH_BUTTON_NARROW").click(timeout=timeout)
        except TimeoutError:
            pass

    @step("Search for: {keyword}")
    def search(self, keyword: str):
        from pages.youtube.search import YouTubeSearchPage

        self.click_search_button_narrow_if_visible()
        self.locator("SEARCH_INPUT").fill(keyword)
        self.locator("SEARCH_BUTTON").first.click()
        return YouTubeSearchPage(self.page)
