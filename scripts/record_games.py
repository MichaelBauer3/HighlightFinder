import logging
import sys
import time
import argparse

from datetime import datetime
from app.data_model.game_context import GameContext
from schedule_reader import ScheduleReader
from app.scrapers import LiveBarnAuth, LiveBarnVideo
from app.config.config import LIVE_BARN_EMAIL, LIVE_BARN_PASSWORD, RECORDINGS_DIR, FIELD_CONFIGS
from app.scrapers.driver_manager import DriverManager
from app.services.live_barn_service import LiveBarnService
from app.services.video_service import VideoService
from app.video import ScreenRecorder, ScoreboardFinder, ScoreboardReader, VideoLoader, ScoreValidator

def build_game_from_args(arguments) -> dict:

    date_str = f"{arguments.year}-{arguments.month:02d}-{arguments.day:02d}"
    date = datetime.strptime(f"{date_str} {arguments.time}", "%Y-%m-%d %H:%M")
    month_and_year =  date.strftime("%B %Y")

    return {
        "team": arguments.team,
        "opponent": arguments.opponent,
        "field": arguments.field,
        "time": arguments.time,
        "date": date_str,
        "game_day": str(arguments.day),
        "game_month": f"{arguments.month:02d}",
        "game_year": str(arguments.year),
        "game_month_and_year": month_and_year,
        "datetime": date.isoformat(),
        "is_home": arguments.is_home
    }


def main(games=None, skip_occurred_check=False):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True
    )

    if games is None:
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
        for gm in games:

            game_context = GameContext.from_game(gm, FIELD_CONFIGS)

            if not skip_occurred_check and not game_context.has_occurred():
                logging.info("Game has yet to occur")
                continue

            recording_path = RECORDINGS_DIR / game_context.file_name
            if recording_path.exists():
                logging.info(f"Recording already exists: {game_context.file_name}, skipping")
                continue

            logging.info(f"Recording game: {gm['team']} vs {gm['opponent']}")

            try:
                # navigate to video
                live_barn_service.get_vod_video(gm)

                # Wait for video to load
                time.sleep(10)

                # Record the game (Adjust 60 to N for N minutes)
                duration = 67 * 60
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

    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument("--team", type=str, required=True)
        parser.add_argument("--opponent", type=str, required=True)
        parser.add_argument("--field", type=str, choices=["East Field", "West Field"], required=True)
        parser.add_argument("--time", type=str, required=True, help="e.g. 6:00")
        parser.add_argument("--day", type=int, required=True)
        parser.add_argument("--month", type=int, required=True)
        parser.add_argument("--year", type=int, default=2026)
        parser.add_argument("--is-home", type=bool, default=False)
        parser.add_argument("--skip-occurred-check", type=bool, default=False)

        args = parser.parse_args()
        game = build_game_from_args(args)
        main(games=[game], skip_occurred_check=args.skip_occurred_check)

    else:
        main()