import logging
import time

from schedule_reader import ScheduleReader
from scrapers import LiveBarnAuth, LiveBarnVideo
from config import LIVE_BARN_EMAIL, LIVE_BARN_PASSWORD, FIELD_CONFIGS
from scrapers.driver_manager import DriverManager
from services.live_barn_service import LiveBarnService
from services.video_service import VideoService
from video import VideoLoader, ScreenRecorder, ScoreboardReader, ScoreValidator
from video.scoreboard_finder import ScoreboardFinder


def main():

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    schedule_reader = ScheduleReader()
    games = schedule_reader.fetch_schedule_from_github()

    if len(games) == 0:
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

            # Get game details
            field = FIELD_CONFIGS[game['field']]
            rotation_angle = field['rotation_angle']
            is_home = game['is_home']

            if is_home:
                config = field['home_score_region']
            else:
                config = field['away_score_region']

            # Log in to LiveBarn and get to the game
            live_barn_service.login()
            live_barn_service.get_vod_video(game)

            # Screen Record the game and save it to data/recordings/{team_name}_{date}.mp4
            team_name = game['team'].lower().replace(' ', '_')
            game_date = game['date']
            file_name = f"{team_name}_{game_date.replace('-', '')}.mp4"

            # Let the game load (We don't want to see the LiveBarn Navigation)
            time.sleep(10)
            video_service.screen_record_for_duration(team_name, game_date, 55 * 60)

            # Stop playing video and log out
            live_barn_service.logout()

            # Load the video
            sample_rate = 1
            for timestamp, frame in video_service.stream_frames(file_name, sample_rate):

                # Process frame recorded video
                score_processed = video_service.process_to_digit(frame, config, rotation_angle)

                # Get score from model
                score = video_service.get_score(score_processed)

                # Validate score for N consecutive frames
                is_valid_score = video_service.validate_score(score)

                # If valid, clip previous N seconds and next M seconds and save the clip
                if is_valid_score:
                    goal_file_name = f"goal_{score}_{team_name}.mp4"
                    video_service.clip_goal(file_name, goal_file_name, (timestamp - 30),30)

            video_service.delete_video(file_name)
            schedule_reader.remove_game(game['team'], game['opponent'], game['datetime'])

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()