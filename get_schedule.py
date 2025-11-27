"""
Runs in GitHub Actions to fetch game schedule
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path

from scrapers.driver_manager import DriverManager
from services.day_smart_service import DaySmartService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_schedule():
    """Fetch schedule using Selenium"""
    from scrapers import DaySmartAuth, DaySmartSchedule
    from config import TEAMS

    email = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('PASSWORD')

    if not email or not password:
        logger.error("Missing credentials in environment variables")
        raise ValueError("EMAIL_ADDRESS and PASSWORD must be set in GitHub Secrets")

    logger.info("Starting schedule fetch...")

    driver = DriverManager.create_driver(headless=True)

    try:

        day_smart_auth = DaySmartAuth(driver, email, password)
        day_smart_schedule = DaySmartSchedule(driver)
        day_smart_service = DaySmartService(day_smart_auth, day_smart_schedule)

        day_smart_service.login()

        day_smart_service.navigate_to_schedule()

        all_games = day_smart_service.get_all_team_games(TEAMS, days=21)

        # Prepare data to save
        schedule_data = {
            'updated_at': datetime.now().isoformat(),
            'fetched_by': 'github-actions',
            'games': all_games,
            'status': 'success',
            'team_count': len(TEAMS),
            'game_count': len(all_games)
        }

        # Save to JSON file in repository root
        output_path = Path('schedule_data.json')
        with open(output_path, 'w') as f:
            json.dump(schedule_data, f, indent=2)

        logger.info(f"Schedule saved to {output_path}")
        logger.info(f"Found {len(all_games)} games for {len(TEAMS)} teams")

        return schedule_data

    except Exception as e:
        logger.error(f"Failed to fetch schedule: {e}")

        # Save error status
        error_data = {
            'updated_at': datetime.now().isoformat(),
            'fetched_by': 'github-actions',
            'games': [],
            'status': 'error',
            'error': str(e)
        }

        with open('schedule_data.json', 'w') as f:
            json.dump(error_data, f, indent=2)

        raise


if __name__ == '__main__':
    fetch_schedule()