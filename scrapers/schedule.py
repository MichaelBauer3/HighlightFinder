from datetime import datetime, timedelta

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import logging

logger = logging.getLogger(__name__)

class DaysSmartSchedule:
    BASE_URL = "https://apps.daysmartrecreation.com/dash/x/#/online/rochester/activities"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def navigate_to_schedule(self):
        """Navigate to the schedule/events page"""
        try:
            logger.info(f"Navigating to activities page: {self.BASE_URL}")
            self.driver.get(self.BASE_URL)

        except TimeoutException as e:
            logger.error(f"Timeout during loading activities: {e}")
            raise Exception(f"Loading activities timed out: {e}")

        except Exception as e:
            logger.error(f"Loading activities failed: {e}")
            raise

    def get_scheduled_games(self, team_name: str, days: int = 7):
        """
        Get games for a specific team in the next N days

        Args:
            team_name (str): Team name to search for (e.g., "Ewoks FC")
            days (int): Number of days ahead to search

        Returns:
            list: List of game dictionaries with date, time, field, opponent info
        """
        logger.info(f"Fetching games for '{team_name}' in next {days} days...")

        try:
            # Wait for table rows to load
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, "//tr[contains(@class, 'ng-star-inserted')]"))
            )

            # Find all game rows
            game_rows = self.driver.find_elements(By.XPATH, "//tr[contains(@class, 'ng-star-inserted')]")
            logger.info(f"Found {len(game_rows)} total games in schedule")

            games = []
            cutoff_date = datetime.now() + timedelta(days=days)

            for row in game_rows:
                try:
                    game_info = self._parse_game_row(row, team_name)

                    if game_info:
                        # Check if game is within date range
                        game_date = datetime.fromisoformat(game_info['datetime'])

                        if datetime.now() <= game_date <= cutoff_date:
                            games.append(game_info)
                            logger.info(
                                f"Found game: {game_info['date']} at {game_info['time']} - {game_info['field']}")

                except Exception as e:
                    logger.debug(f"Skipping row: {e}")
                    continue

            logger.info(f"Found {len(games)} game(s) for '{team_name}'")
            return games

        except Exception as e:
            logger.error(f"Failed to fetch games: {e}")
            return []

    def _parse_game_row(self, row, team_name: str):
        """
        Parse a single game row from the schedule table

        Returns: dict or None: Game information if team is in this game, else None
        """
        try:
            # Extract teams
            team_links = row.find_elements(By.XPATH, ".//dash-event-title//a")

            if len(team_links) < 2:
                return None

            away_team = team_links[0].text.strip().lower()
            home_team = team_links[1].text.strip().lower()

            # Check if our team is in this game
            if team_name not in [away_team, home_team]:
                return None

            is_home = (team_name == home_team)
            opponent = away_team if is_home else home_team

            # Extract date
            date_cell = row.find_element(By.XPATH,
                                         ".//td[@data-sort and contains(@data-sort, '2025') or contains(@data-sort, '2024') "
                                         "or contains(@data-sort, '2026')]")
            date_sort = date_cell.get_attribute('data-sort')  # Format: "2025-12-04T22:00:00"

            # Extract time
            time_cell = row.find_element(By.XPATH, ".//td[contains(text(), 'pm') or contains(text(), 'am')]")
            time_text = time_cell.text.strip()  # Format: "10:00pm - 10:50pm"

            # Extract location/field
            location_cell = row.find_element(By.XPATH, ".//td[contains(text(), 'Field') or contains(text(), 'Garden')]")
            location_text = location_cell.text.strip()  # Format: "Rochester Sports Garden: East Field"

            # Parse datetime
            game_datetime = self._parse_datetime(date_sort)

            # Parse field identifier
            field = self._identify_field(location_text)

            # Build game info dictionary
            game_info = {
                'team': team_name,
                'opponent': opponent,
                'datetime': game_datetime.isoformat(),
                'date': game_datetime.strftime('%Y-%m-%d'),
                'time': game_datetime.strftime('%I:%M %p'),
                'day_of_week': game_datetime.strftime('%A'),
                'field': field,
                'location': location_text,
                'is_home': is_home,
                'display_time': time_text,
            }

            return game_info

        except Exception as e:
            logger.debug(f"Could not parse row: {e}")
            return None

    @staticmethod
    def _parse_datetime(date_sort_attr):
        """
        Parse datetime from data-sort attribute and time text

        Args:
            date_sort_attr: "2025-12-04T22:00:00"

        Returns:
            datetime: Parsed datetime object
        """
        try:
            # Use the data-sort attribute which already has the datetime
            # Format: "2025-12-04T22:00:00"
            dt = datetime.fromisoformat(date_sort_attr.split('.')[0])  # Remove timezone if present
            return dt

        except Exception as e:
            logger.warning(f"Could not parse datetime from '{date_sort_attr}': {e}")

    @staticmethod
    def _identify_field(location_text):
        """
        Identify which field configuration to use based on location text

        Args:
            location_text: "Rochester Sports Garden: East Field"

        Returns:
            str: Field identifier ("East Field" or "West Field")
        """
        location_lower = location_text.lower()

        # Map field names to configuration keys
        # Update these based on your actual field names
        if 'east' in location_lower:
            return 'East Field'
        elif 'west' in location_lower:
            return 'West Field'
        else:
            logger.warning(f"Unknown field in location: {location_text}")
            return 'field_1'

    def get_all_team_games(self, team_names, days=7):
        """
        Get games for multiple teams

        Args:
            team_names (list): List of team names ["Team A", "Team B"]
            days (int): Number of days ahead to search

        Returns:
            list: Combined list of all games for all teams
        """
        all_games = []

        for team_name in team_names:
            games = self.get_scheduled_games(team_name, days)
            all_games.extend(games)

        # Sort by datetime
        all_games.sort(key=lambda g: g['datetime'])

        return all_games