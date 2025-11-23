"""
Runs in GitHub Actions to fetch game schedule
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from config import EMAIL, PASSWORD

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_schedule():
    """Fetch schedule using Selenium"""
    from scrapers import DaysSmartAuth, DaysSmartSchedule
    from config import TEAMS

    email = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('PASSWORD')

    if not email or not password:
        logger.error("Missing credentials in environment variables")
        raise ValueError("EMAIL_ADDRESS and PASSWORD must be set in GitHub Secrets")

    logger.info("Starting schedule fetch...")

    try:
        auth = DaysSmartAuth(email, password, headless=True)
        driver = auth.login()
        scraper = DaysSmartSchedule(driver)

        scraper.navigate_to_schedule()

        all_games = scraper.get_all_team_games(TEAMS, days=7)

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

        # TODO - Delete this
        # Print summary for GitHub Actions log
        print("\n" + "=" * 60)
        print("SCHEDULE FETCH SUMMARY")
        print("=" * 60)
        for game in all_games:
            print(f"  {game['team']}: {game['date']} {game['time']} - {game['field']}")
        print("=" * 60 + "\n")

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