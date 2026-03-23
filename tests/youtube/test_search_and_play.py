import pytest
from playwright.sync_api import expect

from common.constants import VideoReadyState
from pages.youtube.home import YouTubeHomePage


@pytest.fixture
def youtube_home(page):
    return YouTubeHomePage(page)


class TestYouTubeSearch:
    @pytest.mark.smoke
    @pytest.mark.parametrize("search_text", ["mrbeast"])
    def test_search_channel_and_play_video(self, youtube_home: YouTubeHomePage, search_text):
        """Search for a channel on YouTube, navigate to it, play the first video, and verify playback.

        Steps:
        1. Open YouTube home page.
        2. Search for the given keyword.
        3. Click the first channel result to enter the channel page.
        4. Verify the channel page contains at least one video.
        5. Click the first video.
        6. Skip the ad if the skip button appears.
        7. Assert the video reaches at least HAVE_CURRENT_DATA ready state.
        """
        youtube_home.open()
        search_page = youtube_home.search_bar.search(keyword=search_text)
        channel_page = search_page.go_to_channel()
        expect(channel_page.videos.first).to_be_visible()

        page = channel_page.go_to_video(index=3)
        page.skip_ad_if_visible()
        assert page.wait_for_video_state(state=VideoReadyState.HAVE_CURRENT_DATA), (
            "Video did not reach HAVE_CURRENT_DATA state"
        )
