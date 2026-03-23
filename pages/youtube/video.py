from playwright.sync_api import Page, TimeoutError

from common.constants import VideoReadyState
from pages.base import step
from pages.youtube.base import YouTubeBasePage


class YouTubeVideoPage(YouTubeBasePage):
    element_file_path = "youtube/video"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @step("Skip ad if visible")
    def skip_ad_if_visible(self, timeout: int = 5_000):
        try:
            self.locator("AD_SKIP_BUTTON").click(timeout=timeout)
        except TimeoutError:
            pass

    @step("Assert the video reaches at least {state} ready state")
    def wait_for_video_state(
        self,
        state: VideoReadyState,
        timeout: int = 10_000,
    ) -> bool:
        try:
            self.page.wait_for_function(
                """
                (expectedState) => {
                    const video = document.querySelector('video.html5-main-video');
                    return video && video.readyState >= expectedState;
                }
                """,
                arg=int(state),
                timeout=timeout,
            )
            return True
        except TimeoutError:
            return False
