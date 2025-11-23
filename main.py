import json
import logging
import time

from scrapers import LiveBarnAuth, LiveBarnVideo
from scrapers.day_smart_auth import DaySmartAuth
from scrapers.day_smart_schedule import DaySmartSchedule
from config import DAY_SMART_EMAIL, DAY_SMART_PASSWORD, LIVE_BARN_EMAIL, LIVE_BARN_PASSWORD, TEAMS


def main():

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    auth = DaySmartAuth(DAY_SMART_EMAIL, DAY_SMART_PASSWORD, headless=False)
    try:
        driver = auth.login()
        time.sleep(5)

        with open('schedule_data.json') as f:
            schedule = json.load(f)

        if not schedule['games']:
            print("No games in schedule!")
            return

        game = schedule['games'][0]

        live_barn = LiveBarnAuth(LIVE_BARN_EMAIL, LIVE_BARN_PASSWORD, driver)
        live_barn.login()
        live_barn_video = LiveBarnVideo(driver)
        live_barn_video.navigate_to_favorites()
        live_barn_video.navigate_to_games(game)
        time.sleep(10)


    finally:
        auth.logout()

if __name__ == "__main__":
    main()