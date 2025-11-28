from scrapers import LiveBarnAuth, LiveBarnVideo


class LiveBarnService:

    def __init__(self, live_barn_auth: LiveBarnAuth, live_barn_video: LiveBarnVideo):
        self.live_barn_auth = live_barn_auth
        self.live_barn_video = live_barn_video

    def login(self) -> None:
        self.live_barn_auth.login()

    def get_live_video(self, game_data) -> None:
        self.live_barn_video.navigate_to_favorites()
        self.live_barn_video.navigate_to_live_games(game_data)

    def get_vod_video(self, game_data) -> None:
        self.live_barn_video.navigate_to_favorites()
        self.live_barn_video.navigate_to_vod_games(game_data)
        pass