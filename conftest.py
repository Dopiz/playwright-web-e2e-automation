import logging
import os
from pathlib import Path

import allure
import pytest

logger = logging.getLogger("conftest")


def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", default=False)
    parser.addoption("--browser", action="store", default="chromium")
    parser.addoption("--device", action="store", default=None)
    parser.addoption(
        "--env",
        action="store",
        default="default",
        help="Config environment name (default, staging, etc)",
    )


def pytest_configure(config):
    config.artifact_path = Path(__file__).parent / "artifacts"
    os.makedirs(config.artifact_path, exist_ok=True)

    from utils.helper import ConfigHelper

    config_helper = ConfigHelper(env=config.getoption("--env"))
    # logger.info("Env:", config.getoption("--env"))
    logger.info("Config:", config_helper.all)


def pytest_runtest_setup(item):
    logger.info(f"========== START: {item.name} ==========")


def pytest_runtest_teardown(item):
    logger.info(f"========== END: {item.name} ==========\n")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # Store result on node so fixtures can check pass/fail during teardown
    setattr(item, f"rep_{report.when}", report)

    if report.when == "call":
        logger.info(f"Result: {report.outcome.upper()}")
        if report.failed:
            logger.error(f"Failure reason: {report.longreprtext}")

    if report.when != "call":
        return

    page = item.funcargs.get("page")
    if not page:
        return

    case_name = item.name.replace("[", "_").replace("]", "")

    # Screenshot
    try:
        screenshot_path = os.path.join(item.config.artifact_path, f"{case_name}.png")
        screenshot_bytes = page.screenshot(path=screenshot_path, full_page=False)
        allure.attach(
            screenshot_bytes,
            name="Screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        logger.warning("Fail to save screenshot")

    # HTML snapshot (only on failure)
    if not report.failed:
        return

    try:
        html_content = page.content()
        html_path = os.path.join(item.config.artifact_path, f"{case_name}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        allure.attach(html_content, name="Page HTML", attachment_type=allure.attachment_type.HTML)
    except Exception:
        logger.warning("Fail to save HTML snapshot")
