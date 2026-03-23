from playwright.sync_api import Page

from pages.base import step
from pages.youtube.base import YouTubeBasePage


class YouTubeSearchPage(YouTubeBasePage):
    element_file_path = "youtube/search"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @step("Go to channel from search results")
    def go_to_channel(self):
        from pages.youtube.channel import YouTubeChannelPage

        self.locator("CHANNEL_LINK").first.click()
        return YouTubeChannelPage(self.page)
