import pytest
from playwright.sync_api import Browser, BrowserContext, BrowserType, Page, Playwright, sync_playwright

from utils.helper import ConfigHelper


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser_type(playwright_instance: Playwright, request) -> BrowserType:
    browser_name = request.config.getoption("--browser")
    return getattr(playwright_instance, browser_name)


@pytest.fixture(scope="session")
def browser(browser_type: BrowserType, request) -> Browser:
    headless = request.config.getoption("--headless")
    browser = browser_type.launch(headless=headless)
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def browser_context(browser: Browser, playwright_instance: Playwright, request) -> BrowserContext:
    device_name = request.config.getoption("--device")
    if not device_name:
        device_name = ConfigHelper().get("browser").get("device")

    if device_name:
        device = playwright_instance.devices.get(device_name)
        if device is None:
            pytest.fail(f"Unknown device: {device_name}")
        context = browser.new_context(**device)
    else:
        config = ConfigHelper()
        browser_config = config.get("browser")
        viewport_width = browser_config.get("viewport_width")
        viewport_height = browser_config.get("viewport_height")

        context_kwargs = {}
        if viewport_width and viewport_height:
            context_kwargs["viewport"] = {
                "width": viewport_width,
                "height": viewport_height,
            }

        context = browser.new_context(**context_kwargs)
    yield context
    context.close()


@pytest.fixture(scope="session")
def session_page(browser_context: BrowserContext) -> Page:
    page = browser_context.new_page(ignore_https_errors=True)
    # Login / Session / Cookie
    yield page
    page.close()


@pytest.fixture
def page(browser_context: BrowserContext) -> Page:
    config = ConfigHelper()
    default_timeout = config.get("browser").get("default_timeout", 5000)

    page = browser_context.new_page()
    page.set_default_timeout(default_timeout)
    yield page
    page.close()
