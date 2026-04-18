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

    def navigate_to_live_games(self, game_data):
        """Navigate to the Games"""
        logger.info(f"Navigating to game: {game_data['date']} at {game_data['time']}")

        try:
            logger.info(f"Attempting to click RSG")
            self._select_venue()
            logger.info(f"Successfully clicked RSG")

            field = game_data['field']
            logger.info(f"Selecting Field: {field}")
            self._select_field_live(field)

        except Exception as e:
            logger.error(f"Could not select game: {e}")
            raise

    def navigate_to_vod_games(self, game_data):
        """Navigate to the VOD Games"""
        logger.info(f"Navigating to VOD game: {game_data['date']} at {game_data['time']}")

        try:
            logger.info(f"Attempting to click RSG")
            self._select_venue()
            logger.info(f"Successfully clicked RSG")

            field = game_data['field']
            game_time = game_data['time']
            day = game_data['game_day']
            month_year = game_data['game_month_and_year']
            logger.info(f"Selecting Field: {field}")
            self._select_field_vod(field, game_time, day, month_year)

        except Exception as e:
            logger.error(f"Could not select VOD game: {e}")
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

    def _select_field_live(self, field_name):
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

            self._select_fullscreen_pano()

        except Exception as e:
            logger.error(f"Could not select field {field_name}: {e}")
            raise

    def _select_field_vod(self, field_name: str, game_time: str, day: str, month_and_year: str):
        """
        Select specific field/stream after venue is expanded

        Args:
            field_name: "East Field" or "West Field"
            game_time: time of the game
            day: day of the game
            month_and_year: month and year of the game
        """

        try:
            rows = self.driver.find_elements(By.XPATH, f"//tr[.//span[normalize-space()='{field_name}']]")
            row = rows[-1]  # Get the last (most specific) match

            vod_button = row.find_element(By.XPATH, ".//a[.//*[name()='svg']//*[name()='text'][@id='VOD']]")

            vod_button.click()

            logger.info(f"Selected VOD for field: {field_name} on {month_and_year} {day} at {game_time}")
            time.sleep(3)

            self._select_vod_game(game_time, day, month_and_year)

        except Exception as e:
            logger.error(f"Could not select VOD for {field_name}: {e}")
            raise

    def _select_vod_game(self, game_time: str, day: str, month_and_year: str):
        """
        Select specific VOD game after VOD button is clicked

        Args:
            game_time: time of the game
            day: day of the game
            month_and_year: month and year of the game
        """
        month = month_and_year.split(' ')[0]
        try:
            month_and_year_selected = datetime.now().strftime("%B %Y")
            if month_and_year_selected != month_and_year:
                self._get_previous_month()

            day_button = self.wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, f"//div[.//span[text()='{month_and_year}'] and .//span[text()='Sun'] and .//span[text()='Sat']]//div[span[text()='{day}']]")
                )
            )
            day_button.click()
            time.sleep(1)

            time_button = self.wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, f"//span[contains(text(), '{game_time}')]")
                )
            )
            time_button.click()
            time.sleep(1)

            watch_button = self.wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, "//button[text()='Watch']")
                )
            )
            watch_button.click()
            logger.info(f"Selected VOD game on {month} {day} at {game_time}")

            self._select_fullscreen_pano()

        except Exception as e:
            logger.error(f"Could not select VOD game on {month} {day} at {game_time}: {e}")
            raise

    def _get_previous_month(self):
        """
        Get the previous month

        Returns:
            previous True if moved back a month, False otherwise
        """
        try:
            prev_button = self.wait.until(
                ec.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button:has([data-testid='ArrowLeftIcon'])")
                )
            )
            prev_button.click()
            logger.info("Moved to previous month.")
            time.sleep(1)

        except Exception as e:
            logger.error(f"Could not click previous month button: {e}")
            raise

    def _select_fullscreen_pano(self):
        """
        Forces the UI to appear and keeps clicking until Fullscreen/Pano are active.
        """
        logger.info("Executing Bulletproof Pano/Fullscreen sequence.")

        force_ui_script = """
        const triggerUI = () => {
            const video = document.querySelector('video');
            if (video) {
                // Dispatch a move event to trick the player into showing the bar
                video.dispatchEvent(new MouseEvent('mousemove', { bubbles: true }));
            }
        };

        const clickWhenReady = (label) => {
            return new Promise((resolve) => {
                let attempts = 0;
                const interval = setInterval(() => {
                    const btn = document.querySelector(`button[aria-label="${label}"]`);
                    // If button exists and is visible (not hidden by 2.5s timer)
                    if (btn && btn.offsetHeight > 0) {
                        btn.click();
                        clearInterval(interval);
                        resolve(true);
                    } else {
                        triggerUI(); // Keep shaking the mouse every 200ms
                    }

                    if (attempts++ > 25) { // 5-second timeout
                        clearInterval(interval);
                        resolve(false);
                    }
                }, 200);
            });
        };

        // Chain the actions: Pano first, then Fullscreen
        clickWhenReady("Panoramic").then(() => {
            setTimeout(() => clickWhenReady("Fullscreen"), 400);
        });
        """

        try:
            # Wait for the video to actually be 'ready' to receive events
            self.wait.until(ec.presence_of_element_located((By.TAG_NAME, "video")))

            # Run the script
            self.driver.execute_script(force_ui_script)

            # Wait a moment and check if the 'Fullscreen' state was actually achieved
            time.sleep(1.5)
            logger.info("Sequence finished. Scoreboard should now be Fullscreen Pano.")

        except Exception as e:
            logger.error(f"Critical failure in Full Screen / Pano toggle: {e}")