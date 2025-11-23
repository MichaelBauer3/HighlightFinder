import logging
import time

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

logger = logging.getLogger(__name__)

class DaysSmartAuth:

    BASE_URL = "https://apps.daysmartrecreation.com/dash/index.php?Action=Auth/login&company=rochester"

    def __init__(self, email: str, password: str, headless: bool = False):
        self.email = email
        self.password = password
        self.headless = headless
        self.driver = None
        self.is_logged_in = False

    def _setup_chrome_options(self):
        """Configure Chrome options"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless=new')

        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        chrome_options.add_argument('--window-size=1920,1080')

        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        return chrome_options

    def _init_driver(self):
        """Initialize the Chrome WebDriver"""
        try:
            chrome_options = self._setup_chrome_options()
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            raise

    def login(self):
        """Login to DaysSmart"""

        if self.driver is None:
            self._init_driver()

        try:
            logger.info(f"Navigating to login page: {self.BASE_URL}")
            self.driver.get(self.BASE_URL)

            # Wait for page to load
            wait = WebDriverWait(self.driver, 15)

            # Find and fill email field
            logger.info("Locating email field...")
            email_field = wait.until(
                ec.presence_of_element_located((By.NAME, "email"))
            )
            email_field.clear()
            email_field.send_keys(self.email)
            logger.info("Email entered")

            # Find and fill password field
            logger.info("Locating password field...")
            password_field = wait.until(
                ec.presence_of_element_located((By.NAME, "password"))
            )
            password_field.clear()
            password_field.send_keys(self.password)
            logger.info("Password entered")

            logger.info("Locating submit field...")
            submit_button = wait.until(
                ec.element_to_be_clickable((By.NAME, "submit"))
            )
            submit_button.click()
            logger.info("Submit button clicked")

            try:
                wait.until(ec.url_changes(self.BASE_URL))
                time.sleep(2)  # Give the page time to fully load

                try:
                    wait.until(
                        ec.presence_of_element_located(
                            (By.XPATH, "//span[contains(@class, 'dropdown-item') and contains(text(), 'Log out')]")
                        )
                    )
                    self.is_logged_in = True
                    logger.info("Login successful!")
                    return self.driver
                except TimeoutException:
                    logger.warning("Login may have failed - could not verify success")

            except TimeoutException:
                logger.error("Login timed out - URL did not change")
                raise Exception("Login failed - page did not redirect")

            return self.driver

        except TimeoutException as e:
            logger.error(f"Timeout during login: {e}")
            raise Exception(f"Login timed out: {e}")

        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise

    def logout(self):
        """Logout and close the browser"""
        if self.driver:
            try:
                logger.info("Logging out and closing browser...")
                self.driver.quit()
                self.driver = None
                self.is_logged_in = False
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error during logout: {e}")