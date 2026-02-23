import logging

from schedule_reader import ScheduleReader
from config import FIELD_CONFIGS, CLIPS_DIR, RECORDINGS_DIR, METADATA_DIR
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
        is_home = game["is_home"]

        # Check if recording exists
        if not file_path.exists():
            logging.warning(f"Recording not found: {file_name}, skipping")
            continue

        # Check if already processed
        existing_goals = list(CLIPS_DIR.glob(f"goal_*_{team_name}_{game_date}_*.mp4"))
        if existing_goals:
            logging.info(f"Already processed: {file_name}, skipping")
            continue

        logging.info(f"Processing video: {file_name}")

        # Get field configuration
        field = FIELD_CONFIGS[game['field']]
        rotation_angle = field['rotation_angle']
        template = METADATA_DIR / field['template_path']

        video_service.set_template(template)

        config = field['scoreboard_region']
        digit_region = config['home_score_region'] if is_home else config['away_score_region']

        # Process video
        sample_rate = 1
        goals_found = 0

        try:
            for timestamp, frame in video_service.stream_frames(file_name, sample_rate):
                # Process frame
                score_processed = video_service.process_to_digit(frame, config, rotation_angle, digit_region)

                # Get score from model
                score = video_service.get_score(score_processed)

                # Validate score
                is_valid_score, real_score = video_service.validate_score(score)

                # If valid, clip and save
                if is_valid_score:
                    goal_file_name = f"goal_{real_score}_{team_name}_{game_date}.mp4"
                    video_service.clip_goal(file_name, goal_file_name, timestamp - 30, 30)
                    goals_found += 1
                    logging.info(f"Found goal {goals_found}: {real_score}")

            logging.info(f"Processing complete: {file_name}, found {goals_found} goals")

        except Exception as e:
            logging.error(f"Failed to process {file_name}: {e}")

if __name__ == "__main__":
    main()
