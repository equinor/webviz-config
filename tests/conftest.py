# Sets the window size of the browser (crucial in --headless mode).
from selenium.webdriver.chrome.options import Options


def pytest_setup_options():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    return options
