import logging
import sys
import time

from src.app.data_model.game_context import GameContext
from schedule_reader import ScheduleReader
from src.app.scrapers import LiveBarnAuth, LiveBarnVideo
from app.config.config import LIVE_BARN_EMAIL, LIVE_BARN_PASSWORD, RECORDINGS_DIR, FIELD_CONFIGS
from src.app.scrapers.driver_manager import DriverManager
from src.app.services.live_barn_service import LiveBarnService
from src.app.services.video_service import VideoService
from src.app.video import ScreenRecorder, ScoreboardFinder, ScoreboardReader, VideoLoader, ScoreValidator


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
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

        live_barn_service.login()
        for game in games:

            game_context = GameContext.from_game(game, FIELD_CONFIGS)

            # Uncomment these if ML data_model needs more data
            """game['field'] = "East Field"
            game['game_day'] = "12"
            game['time'] = "8:00"
            game['date'] = '2026-03-12'
            game['game_month_and_year'] = "March 2026" """

            # Comment out when testing
            if not game_context.has_occurred():
                logging.info("Game has yet to occur")
                continue

            recording_path = RECORDINGS_DIR / game_context.file_name
            if recording_path.exists():
                logging.info(f"Recording already exists: {game_context.file_name}, skipping")
                continue

            logging.info(f"Recording game: {game['team']} vs {game['opponent']}")

            try:
                # navigate to video
                live_barn_service.get_vod_video(game)

                # Wait for video to load
                time.sleep(10)

                # Record the game (Adjust 60 to N for N minutes)
                duration = 60 * 60
                success = video_service.screen_record_for_duration(recording_path, duration)

                if success:
                    logging.info(f"Successfully recorded: {game_context.file_name}")
                else:
                    logging.error(f"Failed to record: {game_context.file_name}")

                live_barn_service.reset_between_videos()
                time.sleep(10)

            except Exception as e:
                logging.error(f"Failed to record {game_context.file_name}: {e}")

        live_barn_service.logout()
    except Exception as e:
        logging.error(f"Recording job failed: {e}")
    finally:
        DriverManager.close_driver(driver)


if __name__ == "__main__":
    main()