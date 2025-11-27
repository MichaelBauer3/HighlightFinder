import logging
import time

from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

logger = logging.getLogger(__name__)

class LiveBarnAuth:

    BASE_URL = "https://watch.livebarn.com/en/signin"

    def __init__(self, driver: WebDriver, email: str, password: str):
        self.email = email
        self.password = password
        self.driver = driver
        self.is_logged_in = False

    def login(self) -> bool:
        """Login to LiveBarn"""

        try:
            logger.info(f"Navigating to login page: {self.BASE_URL}")
            self.driver.get(self.BASE_URL)

            # Wait for page to load
            wait = WebDriverWait(self.driver, 15)

            # Find and fill email field
            logger.info("Locating username field...")
            username_field = wait.until(
                ec.presence_of_element_located((By.NAME, "username"))
            )
            username_field.clear()
            username_field.send_keys(self.email)
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
                ec.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')]"))
            )
            submit_button.click()
            logger.info("Submit button clicked")

            try:
                wait.until(ec.url_changes(self.BASE_URL))
                time.sleep(2)  # Give the page time to fully load

                try:
                    wait.until(
                        ec.presence_of_element_located(
                            (By.XPATH, "//li[@role='menuitem' and .//span[text()='Log out']]")
                        )
                    )
                    self.is_logged_in = True
                    logger.info("Login successful!")
                    return self.is_logged_in
                except TimeoutException:
                    logger.warning("Login may have failed - could not verify success")
                    return self.is_logged_in

            except TimeoutException:
                logger.error("Login timed out - URL did not change")
                return self.is_logged_in

        except TimeoutException as e:
            logger.error(f"Timeout during login: {e}")
            return self.is_logged_in

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return self.is_logged_in

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