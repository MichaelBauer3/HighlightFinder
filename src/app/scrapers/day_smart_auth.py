import logging
import time

from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

logger = logging.getLogger(__name__)

class DaySmartAuth:

    BASE_URL = "https://apps.daysmartrecreation.com/dash/index.php?Action=Auth/login&company=rochester"

    def __init__(self, driver: WebDriver, email: str, password: str):
        self.email = email
        self.password = password
        self.driver = driver
        self.is_logged_in = False

    def login(self) -> bool:
        """Login to DaysSmart"""
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
                    return self.is_logged_in
                except TimeoutException:
                    logger.warning("Login may have failed - could not verify success")

            except TimeoutException:
                logger.error("Login timed out - URL did not change")
                return self.is_logged_in

            return self.is_logged_in

        except TimeoutException as e:
            logger.error(f"Timeout during login: {e}")
            return self.is_logged_in

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return self.is_logged_in

    def logout(self):
        """Logout and close the browser"""
        if not self.is_logged_in:
            logger.warning("Not logged in, cannot logout.")

        try:
            logger.info("Logging out...")
            wait = WebDriverWait(self.driver, 10)

            logout_button = wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, "//span[contains(@class, 'dropdown-item') and contains(text(), 'Log out')]")
                )
            )
            logout_button.click()

            self.is_logged_in = False
            logger.info("Logout successful!")
            return True

        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False