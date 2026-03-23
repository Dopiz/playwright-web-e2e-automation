from playwright.sync_api import Page

from pages.youtube.base import YouTubeBasePage


class YouTubeHomePage(YouTubeBasePage):
    element_file_path = "youtube/home"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
