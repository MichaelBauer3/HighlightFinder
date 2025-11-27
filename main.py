import json
import logging
import time

import cv2
import numpy as np
from PIL import Image
from pytesseract import pytesseract

from get_schedule import fetch_schedule
from schedule_reader import ScheduleReader
from scrapers import LiveBarnAuth, LiveBarnVideo
from scrapers.day_smart_auth import DaySmartAuth
from scrapers.day_smart_schedule import DaySmartSchedule
from config import DAY_SMART_EMAIL, DAY_SMART_PASSWORD, LIVE_BARN_EMAIL, LIVE_BARN_PASSWORD, TEAMS, FIELD_CONFIGS
from scrapers.driver_manager import DriverManager
from services.day_smart_service import DaySmartService
from services.live_barn_service import LiveBarnService
from services.video_service import VideoService
from video import VideoLoader, ScreenRecorder, ScoreboardReader, scoreboard_reader, ScoreValidator
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

        field = str()
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
            video_service.screen_record_for_duration(3600)
            team_name = game['home_team'].lower().replace(' ', '_')
            file_name = f"{team_name}_{game['date'].replace('-', '')}.mp4"

            # Load the video
            sample_rate = 10
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
                    video_service.clip_goal(file_name, goal_file_name, (timestamp - sample_rate), 25)



    finally:
        driver.quit()

if __name__ == "__main__":
    main()