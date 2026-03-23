# End-to-End Automation Testing Framework

An end-to-end testing framework for YouTube, built with **Playwright** and **Pytest**, following the **Page Object Model (POM)** design pattern.

![Playwright Demo](playwright-demo.gif)

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| [uv](https://github.com/astral-sh/uv) | 0.10.11 | Python package manager |
| [Pytest](https://docs.pytest.org/) | 9.0.2 | Test framework |
| [Playwright](https://playwright.dev/python/) | 1.58.0 | Browser automation |
| [Allure](https://allurereport.org/) | 3.3.1 | Test reporting |
| [Ruff](https://github.com/astral-sh/ruff) | 0.15.7 | Linter & formatter |

## Project Structure

```
.
├── common/
│   └── constants.py                  # Global constants
├── configuration/
│   └── default.yaml                  # Default config (browser, youtube, etc.)
├── elements/
│   └── youtube/                      # YAML-based element selectors
│       ├── channel.yaml
│       ├── home.yaml
│       ├── search.yaml
│       ├── search_bar.yaml
│       └── video.yaml
├── pages/
│   ├── base.py                       # BasePage + @step decorator
│   └── youtube/                      # Page Object Model classes
│       ├── base.py                   # YouTubeBasePage (config, search bar)
│       ├── channel.py
│       ├── home.py
│       ├── search.py
│       ├── search_bar.py            # Shared Component - Search Bar
│       └── video.py
├── test_data/
│   └── youtube/
│       └── search_and_play.yaml      # Test data for search & play tests
├── tests/
│   ├── conftest.py                   # Browser / Context / Page / Data fixtures
│   └── youtube/
│       └── test_search_and_play.py   # YouTube test cases
├── utils/
│   ├── helper.py                     # Config, Element & Data YAML loader
│   └── singleton.py                  # Singleton metaclass
├── conftest.py                       # pytest hooks, logging, allure artifacts
├── pytest.ini                        # Default pytest options & logging
└── requirements.txt
```

## Setup

### 1. Create virtual environment & install dependencies

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Install Playwright browsers

```bash
uv run playwright install
```

### 3. Install pre-commit hooks

```bash
uv pip install pre-commit
uv run pre-commit install
```

This sets up automatic code quality checks on every `git commit`:
- **ruff check** — Linting with auto-fix
- **ruff format** — Code formatting

To run manually on all files:

```bash
uv run pre-commit run --all-files
```

### 4. Run tests

```bash
pytest
```

## Test Options

Custom options defined via `pytest_addoption`:

| Option | Default | Description |
|--------|---------|-------------|
| `--browser` | `chromium` | Browser engine (`chromium`, `firefox`, `webkit`) |
| `--headless` | `False` | Run in headless mode |
| `--device` | `None` | Device emulation (e.g. `"iPhone 12 Pro"`) |
| `--env` | `default` | Config environment name (e.g. `staging`, `mobile`) |

These can be set in `pytest.ini` or passed via CLI:

```bash
# Run with Firefox in headless mode
pytest --browser=firefox --headless

# Run with device emulation
pytest --device="iPhone 12 Pro"

# Run with a specific environment config
pytest --env=staging

# Run a specific test
pytest tests/youtube/test_search_and_play.py::TestYouTubeSearch::test_search_channel_and_play_video
```

## Allure Report

### Generate & view report

```bash
# Run tests with allure results (enabled by default in pytest.ini)
pytest --alluredir=allure-results

# Generate and open report
allure serve allure-results
```

### Report includes

- **Test steps** — Each Page Object action is automatically logged as an Allure step via `@step` decorator
- **Screenshots** — Captured after every test (pass or fail)
- **HTML snapshots** — Page HTML saved on test failure for debugging

## Design Highlights

### YAML-based Element Management

Selectors are stored in YAML files under `elements/`, decoupled from page logic. When the UI changes, update the YAML — no need to touch Python code.

```yaml
# elements/youtube/channel.yaml
VIDEOS: "//ytd-grid-video-renderer//a[@id='video-title']"
```

### Page Object Model with Component Composition

- **BasePage** provides shared utilities (`locator`, `open`, `scroll`)
- **SearchBarComponent** is composed into pages that need it, avoiding inheritance duplication
- **Actions** return the next Page Object for fluent chaining
- **Properties** expose raw `Locator` objects — assertions stay in tests

```python
youtube_home.open()
search_page = youtube_home.search_bar.search(keyword="mrbeast")
channel_page = search_page.go_to_channel()
page = channel_page.go_to_video(index=0)
```

### YAML-based Test Data Management

Test data is stored in YAML files under `test_data/`, decoupled from test logic. Add test cases by editing YAML — no need to touch Python code.

```yaml
# test_data/youtube/search_and_play.yaml
search_and_play:
  - keyword: "mrbeast"
    video_index: 3
    description: "Search MrBeast channel and play video"
    is_skip: false

  - keyword: "aespa"
    video_index: 0
    description: "Search aespa channel and play video"
    is_skip: true
    skip_reason: "Channel structure differs"
```

Each test case supports:

| Field | Required | Description |
|-------|----------|-------------|
| `description` | Yes | Displayed in test name and Allure report |
| `is_skip` | Yes | Set `true` to skip this case |
| `skip_reason` | No | Reason shown when skipped |
| Other fields | - | Custom data used by the test |

Tests use `indirect=True` parametrize with a shared `data` fixture that automatically handles skip logic and Allure description:

```python
test_data = DataHelper().read("youtube/search_and_play")

class TestYouTubeSearch:
    @pytest.mark.parametrize(
        "data",
        test_data["search_and_play"],
        ids=lambda d: d["description"],
        indirect=True,
    )
    def test_search_channel_and_play_video(self, data, youtube_home):
        youtube_home.open()
        search_page = youtube_home.search_bar.search(keyword=data["keyword"])
        ...
```

### Automatic Artifact Collection

The root `conftest.py` hooks into pytest's reporting to automatically capture screenshots and HTML snapshots, attached to Allure reports for easy debugging.



## Test Filtering

### `-m` (marker)

Run tests by marker. Markers are defined in `pytest.ini`.

| Marker | Description |
|--------|-------------|
| `smoke` | Quick sanity tests for critical paths |
| `regression` | Full regression test suite |
| `slow` | Tests that take a long time to run |

```bash
# Run only smoke tests
pytest -m smoke

# Run smoke but exclude slow tests
pytest -m "smoke and not slow"

# Run smoke or regression
pytest -m "smoke or regression"
```

Mark a test with decorator:

```python
@pytest.mark.smoke
def test_login():
    ...
```

### `-k` (keyword)

Filter tests by name pattern matching (test name, class name, or module name).

```bash
# Run tests with "search" in the name
pytest -k "search"

# Run tests containing "search" but not "channel"
pytest -k "search and not channel"

# Run tests in a specific class
pytest -k "TestYouTubeSearch"

# Combine with marker
pytest -m smoke -k "search"
```

### Key differences

| | `-m` (marker) | `-k` (keyword) |
|---|---|---|
| Filters by | Decorator-based markers | Test/class/module name |
| Needs setup | Yes (`pytest.ini` + `@pytest.mark`) | No |
| Use case | Categorizing tests | Quick ad-hoc filtering |