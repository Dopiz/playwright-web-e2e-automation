# End-to-End Automation Testing Framework

A scalable end-to-end testing framework built with **Playwright** and **Pytest**, following the **Page Object Model (POM)** design pattern. Uses YouTube as a demo target.

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
├── .github/workflows/
│   ├── claude-code-review.yml        # AI-powered PR code review
│   └── test-and-report.yml           # CI test & Allure report
├── common/
│   ├── constants.py                  # Global constants
│   └── ...
├── configuration/
│   ├── default.yaml                  # Default config (browser, youtube, etc.)
│   ├── staging.yaml                  # Staging environment overrides
│   ├── mobile.yaml                   # Mobile device preset
│   └── ...
├── elements/
│   ├── youtube/                      # YAML-based element selectors
│   │   ├── channel.yaml
│   │   ├── home.yaml
│   │   ├── search.yaml
│   │   ├── search_bar.yaml
│   │   ├── video.yaml
│   │   └── ...
│   └── ...
├── pages/
│   ├── base.py                       # BasePage + @step decorator
│   ├── youtube/                      # Page Object Model classes
│   │   ├── base.py                   # YouTubeBasePage (config, search bar)
│   │   ├── channel.py
│   │   ├── home.py
│   │   ├── search.py
│   │   ├── search_bar.py             # Shared Component - Search Bar
│   │   ├── video.py
│   │   └── ...
│   └── ...                           # Other Page Object Model classes
├── test_data/
│   └── youtube/                      # YAML-based test data
│       ├── search_and_play.yaml
│       └── ...
├── tests/
│   ├── conftest.py                   # Browser / Context / Page / Data fixtures
│   └── youtube/
│       ├── test_search_and_play.py   # YouTube test cases
│       └── ...
├── utils/
│   ├── helper.py                     # Config, Element & Data YAML loader
│   ├── singleton.py                  # Singleton metaclass
│   └── ...
├── conftest.py                       # pytest hooks, logging, allure artifacts
├── pyproject.toml                    # Protect configuration (e.g. ruff)
├── pytest.ini                        # Default pytest options & logging
├── .pre-commit-config.yaml           # Pre-commit hooks (ruff)
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

This sets up automatic code quality checks on every `git commit`:
- **ruff check** — Linting with auto-fix
- **ruff format** — Code formatting

To run manually on all files:

### 3. Run tests

```bash
pytest
```

### 4. (Optional) Install pre-commit hooks

```bash
uv pip install pre-commit
uv run pre-commit install
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

- [Report Demo](https://dopiz.github.io/playwright-web-e2e-automation/)

### Install Allure CLI

**[Allure 2](https://allurereport.org/):**

```bash
# macOS
brew install allure

# npm
npm install -g allure-commandline
```

**[Allure 3](https://github.com/allure-framework/allure3):**

```bash
# npm
npm install -g allure-commandline@next
```

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

### Playwright Tracing

Tracing is automatically recorded for every test. On failure, the trace file is saved to `artifacts/{test_name}.zip`. On pass, the trace is discarded.

```bash
# View a trace file
playwright show-trace artifacts/test_search_channel_and_play_video_mrbeast_.zip
```

Trace Viewer includes:

| Feature | Description |
|---------|-------------|
| Action timeline | Step-by-step screenshots of every Playwright action |
| DOM snapshot | Inspect elements like DevTools at each step |
| Network requests | All HTTP requests/responses during the test |
| Console logs | Browser console output |
| Source code | Maps each action back to the test code |

```bash
# View a trace file
playwright show-trace artifacts/test_search_channel_and_play_video_mrbeast_.zip
```

Trace Viewer includes: action timeline with screenshots, DOM snapshots, network requests, and console logs.

### Rerun on Failure

Flaky tests can be automatically retried using `pytest-rerunfailures`. Mark individual tests:

```python
@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_example():
    ...
```

Or apply globally via CLI:

```bash
pytest --reruns 2 --reruns-delay 1
```



## Test Filtering

### `-m` (marker)

Run tests by marker. Markers are defined in `pytest.ini`.

| Marker | Description |
|--------|-------------|
| `smoke` | Quick sanity tests for critical paths |
| `regression` | Full regression test suite |
| `slow` | Tests that take a long time to run |
| `flaky` | Tests that may fail intermittently and need reruns |

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

## CI/CD

### Test & Allure Report (`test-and-report.yml`)

Triggered on push to `main` or manually via `workflow_dispatch`.

1. **Test** — Sets up Python + Playwright, runs tests in headless mode, uploads `allure-results`
2. **Report** — Generates Allure report and deploys to [GitHub Pages](https://dopiz.github.io/playwright-web-e2e-automation/)

### Claude Code Review (`claude-code-review.yml`)

Triggered on pull request (opened, synchronize, reopened).

- Uses [Claude Code Action](https://github.com/anthropics/claude-code-action) to review PR changes
- Posts inline comments on code issues
- Submits review (approve / request changes / comment)
- Checks: Playwright best practices, POM patterns, Ruff code style, YAML config consistency

Required secret: `ANTHROPIC_API_KEY` (`GITHUB_TOKEN` is provided automatically by GitHub Actions)
