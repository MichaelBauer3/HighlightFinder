import logging
from pathlib import Path
from schedule_reader import ScheduleReader
from config import FIELD_CONFIGS, CLIPS_DIR, RECORDINGS_DIR
from video import VideoLoader, ScoreboardReader, ScoreValidator, ScreenRecorder
from video.scoreboard_finder import ScoreboardFinder
from services.video_service import VideoService


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    schedule_reader = ScheduleReader()
    games = schedule_reader.fetch_schedule_from_github()

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

    for game in games:
        team_name = game['team'].lower().replace(' ', '_')
        game_date = game['date'].replace('-', '')
        file_name = f"{team_name}_{game_date}.mp4"
        file_path = RECORDINGS_DIR / file_name

        # Check if recording exists
        if not file_path.exists():
            logging.warning(f"Recording not found: {file_name}, skipping")
            continue

        # Check if already processed
        existing_goals = list(CLIPS_DIR.glob(f"goal_*_{team_name}_{game_date}_*.mp4"))
        if existing_goals:
            logging.info(f"Already processed: {file_name}, skipping")
            # Clean up original recording
            video_service.delete_video(file_name)
            continue

        logging.info(f"Processing video: {file_name}")

        # Get field configuration
        field = FIELD_CONFIGS[game['field']]
        rotation_angle = field['rotation_angle']
        is_home = False
        config = field['home_score_region'] if is_home else field['away_score_region']

        # Process video
        sample_rate = 1
        goals_found = 0

        try:
            for timestamp, frame in video_service.stream_frames(file_name, sample_rate):
                # Process frame
                score_processed = video_service.process_to_digit(frame, config, rotation_angle)

                # Get score from model
                score = video_service.get_score(score_processed)

                # Validate score
                is_valid_score = video_service.validate_score(score)

                # If valid, clip and save
                if is_valid_score:
                    goal_file_name = f"goal_{score}_{team_name}_{game_date}_{goals_found}.mp4"
                    video_service.clip_goal(file_name, goal_file_name, timestamp - 30, 30)
                    goals_found += 1
                    logging.info(f"Found goal {goals_found}: {score}")

            logging.info(f"Processing complete: {file_name}, found {goals_found} goals")

            # Delete original recording after successful processing
            video_service.delete_video(file_name)

        except Exception as e:
            logging.error(f"Failed to process {file_name}: {e}")

if __name__ == "__main__":
    main()
