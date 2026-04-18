import argparse
import logging
import sys
from datetime import datetime

from app.clip_exporter.drive_runner import DriveRunner
from app.data_model.game_context import GameContext
from app.clip_exporter.email_sender import EmailSender
from app.data_model.score_region import ScoreRegion
from schedule_reader import ScheduleReader
from app.config.config import FIELD_CONFIGS, CLIPS_DIR, RECORDINGS_DIR, METADATA_DIR
from app.services.clip_exporter_service import ClipExporterService
from app.video import VideoLoader, ScoreboardReader, ScoreValidator, ScreenRecorder
from app.video import ScoreboardFinder
from app.services.video_service import VideoService


def build_game_from_args(arguments) -> dict:
    return {
        "team": arguments.team,
        "opponent": arguments.opponent,
        "field": arguments.field,
        "date": f"{arguments.date[:4]}-{arguments.date[4:6]}-{arguments.date[6:]}",
        "game_day": arguments.date[6:],
        "game_month": arguments.date[4:6],
        "game_year": arguments.date[:4],
        "is_home": arguments.is_home,
        "datetime": datetime.now().isoformat()
    }


def main(games=None, reprocess=False):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    if games is None:
        schedule_reader = ScheduleReader()
        games = schedule_reader.fetch_schedule_from_github()

    sender = EmailSender()
    drive_runner = DriveRunner()

    video_service = VideoService(
        ScoreboardFinder(),
        ScoreboardReader(),
        ScreenRecorder(),
        VideoLoader(),
        ScoreValidator()
    )

    clip_exporter_service = ClipExporterService(drive_runner, sender)

    folder_paths = []
    for gm in games:
        game_context = GameContext.from_game(gm, FIELD_CONFIGS)
        template_path = METADATA_DIR / game_context.field['template_path']

        if not (RECORDINGS_DIR / game_context.file_name).exists():
            logging.warning(f"Recording not found: {game_context.file_name}, skipping")
            continue

        clip_subdir = CLIPS_DIR / game_context.clip_folder_name()
        folder_paths.append(clip_subdir)

        existing_goals = list(clip_subdir.glob(
            f"goal_*_{game_context.team_name}_{game_context.game_date}.mp4"
        ))
        if existing_goals and not reprocess:
            logging.info(f"Already processed: {game_context.file_name}, skipping")
            continue

        logging.info(f"Processing video: {game_context.file_name}")
        video_service.set_template(template_path)
        digit_region = ScoreRegion.HOME if game_context.is_home else ScoreRegion.AWAY
        goals_found = 0

        try:
            for timestamp, frame in video_service.stream_frames(game_context.file_name, sample_rate=1):
                digit_processed = video_service.get_digit_region(
                    frame,
                    game_context.field,
                    digit_region
                )
                digit_processed = digit_processed[digit_region]

                if digit_processed is None:
                    continue

                score = video_service.get_score(digit_processed)
                is_valid_score, real_score = video_service.validate_score(score)

                if is_valid_score:
                    video_service.clip_goal(game_context, real_score, timestamp - 30, 30)
                    goals_found += 1
                    logging.info(f"Found goal {goals_found}: {real_score}")

            logging.info(f"Processing complete: {game_context.file_name}, found {goals_found} goals")

            if goals_found > 0:
                link = clip_exporter_service.upload_folder(clip_subdir)
                clip_exporter_service.send_highlights(folder_paths, link)

        except Exception as e:
            logging.error(f"Failed to process {game_context.file_name}: {e}")

        finally:
            video_service.reset_after_game()


if __name__ == "__main__":

    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument("--team", type=str, required=True)
        parser.add_argument("--opponent", type=str, required=True)
        parser.add_argument("--field", type=str, choices=["East Field", "West Field"], required=True)
        parser.add_argument("--date", type=str, required=True, help="e.g. 20260416")
        parser.add_argument("--is-home", required=True, default=False)
        parser.add_argument("--reprocess", required=True, help="Skip already processed check", default=True)

        args = parser.parse_args()
        game = build_game_from_args(args)
        main(games=[game], reprocess=args.reprocess)
    else:
        main()