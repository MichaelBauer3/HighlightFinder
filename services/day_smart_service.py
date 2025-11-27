from scrapers import DaySmartAuth, DaySmartSchedule


class DaySmartService:

    def __init__(self, day_smart_auth: DaySmartAuth, day_smart_schedule: DaySmartSchedule):
        self.day_smart_auth = day_smart_auth
        self.day_smart_schedule = day_smart_schedule

    def login(self):
        self.day_smart_auth.login()

    def logout(self) -> None:
        self.day_smart_auth.logout()

    def navigate_to_schedule(self) -> None:
        self.day_smart_schedule.navigate_to_schedule()

    def get_all_team_games(self, team_names, days=7) -> list:
        return self.day_smart_schedule.get_all_team_games(team_names, days)
