import time
from datetime import datetime

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import logging

logger = logging.getLogger(__name__)

class LiveBarnVideo:

    BASE_URL = "https://watch.livebarn.com/en/favorite"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def navigate_to_favorites(self):
        """Navigate to the Favorites"""
        try:
            logger.info(f"Navigating to activities page: {self.BASE_URL}")
            self.driver.get(self.BASE_URL)

        except TimeoutException as e:
            logger.error(f"Timeout during loading favorites: {e}")
            raise Exception(f"Loading favorites timed out: {e}")

        except Exception as e:
            logger.error(f"Loading favorites failed: {e}")
            raise

    def navigate_to_games(self, game_data):
        """Navigate to the Games"""
        logger.info(f"Navigating to game: {game_data['date']} at {game_data['time']}")

        try:
            logger.info(f"Attempting to click RSG")
            self._select_venue()
            logger.info(f"Successfully clicked RSG")

            field = game_data['field']
            logger.info(f"Selecting Field: {field}")
            self._select_field(field)

        except Exception as e:
            logger.error(f"Could not select game: {e}")
            raise

    def _select_venue(self):
        """
        Select RSG to expand options
        """
        try:
            # Click RSG
            venue_cell = self.wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, "//td[text()='Rochester Sports Garden']")
                )
            )
            venue_cell.click()
        except TimeoutException as e:
            logger.error(f"Timeout during clicking venue: {e}")

    def _select_field(self, field_name):
        """
        Select specific field/stream after venue is expanded

        Args:
            field_name: "East Field" or "West Field"
        """

        try:
            # Wait for and click the LIVE Button for field
            self.wait.until(
                ec.presence_of_element_located(
                    (By.XPATH, f"//*[contains(text(), '{field_name}')]")
                )
            )

            live_button = self.wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, f"//tr[.//span[text()='{field_name}']]//*[local-name()='svg' and .//*[text()='LIVE']]")
                )
            )
            live_button.click()
            logger.info(f"Selected LIVE for field: {field_name}")
            time.sleep(3)

            fullscreen_button = self.wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, "//button[@type='button' and @aria-label='Fullscreen']")
                )
            )
            fullscreen_button.click()
            logger.info("Watching in Fullscreen")

        except Exception as e:
            logger.error(f"Could not select field {field_name}: {e}")
            raise