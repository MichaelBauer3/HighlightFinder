import logging
import json
import requests
from datetime import datetime
from pathlib import Path
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/laptop_scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from config import GITHUB_USERNAME, GITHUB_REPO, GITHUB_BRANCH

SCHEDULE_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}/schedule_data.json"


class ScheduleReader:
    """Manages game recordings based on GitHub schedule"""

    def __init__(self):
        self.schedule_cache = Path("data/metadata/schedule_cache.json")
        self.scheduled_games = []

    def fetch_schedule_from_github(self):
        """Download schedule from GitHub repository"""
        logger.info("Fetching schedule from GitHub...")
        logger.info(f"URL: {SCHEDULE_URL}")

        try:
            response = requests.get(SCHEDULE_URL, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('status') == 'success':
                games = data.get('games', [])
                logger.info(f"Fetched {len(games)} games from GitHub")
                logger.info(f"Last updated: {data.get('updated_at')}")

                # Cache the schedule locally
                self._save_schedule_cache(data)

                return games
            else:
                logger.warning(f"GitHub schedule status: {data.get('status')}")
                logger.warning(f"Error: {data.get('error', 'Unknown')}")
                return self._load_schedule_cache()

        except requests.RequestException as e:
            logger.error(f"Failed to fetch from GitHub: {e}")
            logger.info("Falling back to cached schedule...")
            return self._load_schedule_cache()

    def _save_schedule_cache(self, data):
        """Save schedule to local cache"""
        self.schedule_cache.parent.mkdir(parents=True, exist_ok=True)

        with open(self.schedule_cache, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info("Schedule cached locally")

    def _load_schedule_cache(self):
        """Load schedule from local cache"""
        try:
            if self.schedule_cache.exists():
                with open(self.schedule_cache) as f:
                    data = json.load(f)
                logger.info(f"Loaded cached schedule from {data.get('updated_at')}")
                return data.get('games', [])
        except Exception as e:
            logger.error(f"Could not load cache: {e}")

        return []

    def show_upcoming_games(self):
        """Display scheduled games"""
        if not self.scheduled_games:
            logger.info("No games scheduled")
            return

        logger.info("\nUpcoming Games:")
        for game in self.scheduled_games:
            dt = datetime.fromisoformat(game['datetime'])
            if dt > datetime.now():
                logger.info(f"{game['team']}: {dt.strftime('%A %m/%d at %I:%M %p')} - {game['field']}")

    def schedule_all_games(self):
        """Fetch schedule and display games"""
        logger.info("=" * 60)
        logger.info("FETCHING SCHEDULE")
        logger.info("=" * 60)

        games = self.fetch_schedule_from_github()

        if not games:
            logger.warning("No games to schedule")
            return

        self.scheduled_games = games

        logger.info("=" * 60)
        logger.info(f"Found {len(games)} game(s)")
        logger.info("=" * 60)

        self.show_upcoming_games()


if __name__ == "__main__":
    import sys

    scheduler = ScheduleReader()

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode: just fetch and display
        scheduler.schedule_all_games()
    else:
        # Normal mode
        scheduler.schedule_all_games()