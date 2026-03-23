import allure
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
    """Authenticated page that persists across all tests in the session.

    Usage:
        1. Perform login (e.g. page.goto, fill credentials, click submit)
        2. Save state: browser_context.storage_state(path="auth/youtube.json")
        3. For subsequent runs, load state in browser_context fixture:
           browser.new_context(storage_state="auth/youtube.json")
    """
    page = browser_context.new_page(ignore_https_errors=True)
    # TODO: Add login flow here when tests require authentication
    yield page
    page.close()


@pytest.fixture
def data(request) -> dict:
    """Indirect parametrize fixture that handles is_skip and allure description."""
    data = request.param
    if data.get("is_skip"):
        pytest.skip(reason=data.get("skip_reason", "Skipped by test data"))
    allure.dynamic.description(data["description"])
    return data


@pytest.fixture
def page(browser_context: BrowserContext, request) -> Page:
    config = ConfigHelper()
    default_timeout = config.get("browser").get("default_timeout", 5000)

    browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)

    page = browser_context.new_page()
    page.set_default_timeout(default_timeout)
    yield page
    page.close()

    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    if failed:
        case_name = request.node.name.replace("[", "_").replace("]", "")
        trace_path = request.config.artifact_path / f"{case_name}.zip"
        browser_context.tracing.stop(path=str(trace_path))
    else:
        browser_context.tracing.stop()
