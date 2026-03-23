from playwright.sync_api import Page

from pages.base import step
from pages.youtube.base import YouTubeBasePage


class YouTubeChannelPage(YouTubeBasePage):
    element_file_path = "youtube/channel"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def videos(self):
        return self.locator("VIDEOS")

    @step("Go to video at index {index}")
    def go_to_video(self, index: int = 0):
        from pages.youtube.video import YouTubeVideoPage

        elem = self.locator("VIDEOS").nth(index)
        # elem.scroll_into_view_if_needed(timeout=3_000)
        elem.click()
        return YouTubeVideoPage(self.page)
