import logging
import sys

from clip_exporter.drive_runner import DriveRunner
from data_model.game_context import GameContext
from clip_exporter.email_sender import EmailSender
from data_model.score_region import ScoreRegion
from schedule_reader import ScheduleReader
from config import FIELD_CONFIGS, CLIPS_DIR, RECORDINGS_DIR, METADATA_DIR
from services.clip_exporter_service import ClipExporterService
from video import VideoLoader, ScoreboardReader, ScoreValidator, ScreenRecorder
from video.scoreboard_finder import ScoreboardFinder
from services.video_service import VideoService


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    schedule_reader = ScheduleReader()
    games = schedule_reader.fetch_schedule_from_github()

    sender = EmailSender()
    drive_runner = DriveRunner()

    scoreboard_finder = ScoreboardFinder()
    scoreboard_reader = ScoreboardReader()
    video_loader = VideoLoader()
    score_validator = ScoreValidator()
    screen_recorder = ScreenRecorder()

    video_service = VideoService(
        scoreboard_finder,
        scoreboard_reader,
        screen_recorder,
        video_loader,
        score_validator
    )

    clip_exporter_service = ClipExporterService(
        drive_runner,
        sender
    )

    folder_paths = []
    for game in games:

        # Uncomment for testing
        #game['field'] = "East Field"

        game_context = GameContext.from_game(game, FIELD_CONFIGS)
        template_path = METADATA_DIR / game_context.field['template_path']
        anchor_template_path = METADATA_DIR / game_context.field['score_anchor_template_path']

        # Check if recording exists
        if not (RECORDINGS_DIR / game_context.file_name).exists():
            logging.warning(f"Recording not found: {game_context.file_name}, skipping")
            continue

        # Check if already processed
        clip_subdir = CLIPS_DIR / game_context.clip_folder_name()
        folder_paths.append(clip_subdir)
        existing_goals = list(clip_subdir.glob(f"goal_*_{game_context.team_name}_{game_context.game_date}.mp4"))
        if existing_goals:
            logging.info(f"Already processed: {game_context.file_name}, skipping")
            continue

        logging.info(f"Processing video: {game_context.file_name}")

        video_service.set_template(template_path, anchor_template_path)

        digit_region = ScoreRegion.HOME if game_context.is_home else ScoreRegion.AWAY

        # Process video
        sample_rate = 1
        goals_found = 0

        try:
            for timestamp, frame in video_service.stream_frames(game_context.file_name, sample_rate):

                # Process frame
                digit_processed = video_service.get_digit_region(
                    frame,
                    game_context.field,
                    digit_region
                )
                digit_processed = digit_processed[digit_region]

                if digit_processed is None:
                    continue

                # Get score from data_model
                score = video_service.get_score(digit_processed)

                # Validate score
                is_valid_score, real_score = video_service.validate_score(score)

                # If valid, clip and save
                if is_valid_score:
                    video_service.clip_goal(game_context, real_score, timestamp - 30, 30)
                    goals_found += 1
                    logging.info(f"Found goal {goals_found}: {real_score}")

            logging.info(f"Processing complete: {game_context.file_name}, found {goals_found} goals")

            # Send Google Drive Upload Link
            link = clip_exporter_service.upload_folder(clip_subdir)
            clip_exporter_service.send_highlights(folder_paths, link)

        except Exception as e:
            logging.error(f"Failed to process {game_context.file_name}: {e}")

if __name__ == "__main__":
    main()
