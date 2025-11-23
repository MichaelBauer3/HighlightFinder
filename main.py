import logging
import time

from scrapers.auth import DaysSmartAuth
from scrapers.schedule import DaysSmartSchedule
from config import EMAIL, PASSWORD, TEAMS


def main():

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    auth = DaysSmartAuth(EMAIL, PASSWORD, headless=True)
    try:
        driver = auth.login()
        time.sleep(5)

        sched_scraper = DaysSmartSchedule(driver)

        sched_scraper.navigate_to_schedule()
        games = sched_scraper.get_scheduled_games(TEAMS[0], 21)

        print(games)

    finally:
        auth.logout()

if __name__ == "__main__":
    main()