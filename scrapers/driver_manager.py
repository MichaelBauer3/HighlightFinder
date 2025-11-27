import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

logger = logging.getLogger(__name__)

class DriverManager:

    @staticmethod
    def create_chrome_options(headless: bool = False) -> Options:
        """Configure Chrome options"""
        chrome_options = Options()

        if headless:
            chrome_options.add_argument('--headless=new')

        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        return chrome_options

    @staticmethod
    def create_driver(headless: bool = False) -> WebDriver:
        """Initialize the Chrome WebDriver"""
        try:
            chrome_options = DriverManager.create_chrome_options(headless)
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            driver.maximize_window()
            logger.info("Chrome WebDriver initialized successfully")
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            raise

    @staticmethod
    def close_driver(driver: WebDriver) -> None:
        """Close the Chrome WebDriver"""
        if driver:
            try:
                logger.info("Closing browser...")
                driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")