from enum import IntEnum


class VideoReadyState(IntEnum):
    """HTMLMediaElement readyState values.

    0: No data available.
    1: Duration and dimensions are available.
    2: Current frame is available.
    3: Current and next frame available, playback possible.
    4: Enough data buffered for smooth playback.
    """

    def __str__(self):
        return self.name

    HAVE_NOTHING = 0
    HAVE_METADATA = 1
    HAVE_CURRENT_DATA = 2
    HAVE_FUTURE_DATA = 3
    HAVE_ENOUGH_DATA = 4
