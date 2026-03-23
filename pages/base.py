import functools
import logging
from typing import Optional

import allure
from playwright.sync_api import Locator, Page

from utils.helper import ConfigHelper, ElementHelper

logger = logging.getLogger("base_page")


def step(description: str):
    """Decorator that combines allure.step + logging."""

    def decorator(func):
        @functools.wraps(func)
        @allure.step(description)
        def wrapper(*args, **kwargs):
            logger.info(f"Step: {description.format(**kwargs)}", stacklevel=3)
            return func(*args, **kwargs)

        return wrapper

    return decorator


class BasePage:
    element_file_path: Optional[str] = None

    def __init__(self, page: Page) -> None:
        self.page = page
        self._config = ConfigHelper()
        if self.element_file_path is not None:
            self.elements = ElementHelper().read(self.element_file_path)

    def open(self, url: str = ""):
        self.page.goto(
            url,
            wait_until="domcontentloaded",
        )

    def locator(self, element_key: str, **kwargs) -> Locator:
        element = self.elements[element_key]
        if isinstance(element, dict):
            element = element.get(self._config.connection_mode, element)
        if kwargs and isinstance(element, str):
            element = element.format(**kwargs)
        return self.page.locator(element)

    def scroll(self, times: int = 1, delta: int = 300):
        for _ in range(times):
            self.page.mouse.wheel(0, delta)
