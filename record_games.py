import logging
import time

from selenium.common import TimeoutException

from schedule_reader import ScheduleReader
from scrapers import LiveBarnAuth, LiveBarnVideo
from config import LIVE_BARN_EMAIL, LIVE_BARN_PASSWORD
from scrapers.driver_manager import DriverManager
from services.live_barn_service import LiveBarnService
from services.video_service import VideoService
from video import ScreenRecorder, ScoreboardFinder, ScoreboardReader, VideoLoader, ScoreValidator


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    schedule_reader = ScheduleReader()
    games = schedule_reader.fetch_schedule_from_github()

    if len(games) == 0:
        logging.info("No games scheduled")
        return

    driver = DriverManager.create_driver()

    try:
        live_barn_auth = LiveBarnAuth(driver, LIVE_BARN_EMAIL, LIVE_BARN_PASSWORD)
        live_barn_video = LiveBarnVideo(driver)

        scoreboard_finder = ScoreboardFinder()
        scoreboard_reader = ScoreboardReader()
        screen_recorder = ScreenRecorder()
        video_loader = VideoLoader()
        score_validator = ScoreValidator()

        live_barn_service = LiveBarnService(live_barn_auth, live_barn_video)
        video_service = VideoService(
            scoreboard_finder,
            scoreboard_reader,
            screen_recorder,
            video_loader,
            score_validator)

        for game in games:
            team_name = game['team'].lower().replace(' ', '_')
            game_date = game['date'].replace('-', '')
            file_name = f"{team_name}_{game_date}.mp4"

            # Check if already recorded
            recording_path = screen_recorder.output_dir / file_name
            if recording_path.exists():
                logging.info(f"Recording already exists: {file_name}, skipping")
                continue

            logging.info(f"Recording game: {game['team']} vs {game['opponent']}")

            try:
                # Log in and navigate to video
                live_barn_service.login()
                live_barn_service.get_vod_video(game)

                # Wait for video to load
                time.sleep(10)

                # Record the game (Adjust 60 to N for N minutes)
                duration = 60 * 60
                success = video_service.screen_record_for_duration(team_name, duration)

                if success:
                    logging.info(f"Successfully recorded: {file_name}")
                else:
                    logging.error(f"Failed to record: {file_name}")

            except Exception as e:
                logging.error(f"Failed to record {file_name}: {e}")
            finally:
                try:
                    live_barn_service.logout()
                except TimeoutException as e:
                    pass

    except Exception as e:
        logging.error(f"Recording job failed: {e}")
    finally:
        DriverManager.close_driver(driver)


if __name__ == "__main__":
    main()