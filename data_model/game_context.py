from dataclasses import dataclass
from datetime import datetime

@dataclass
class GameContext:
    team_name: str
    game_date: str
    file_name: str
    field: dict
    is_home: bool
    datetime: datetime

    @classmethod
    def from_game(cls, game: dict, field_configs: dict) -> "GameContext":
        """Factory method - builds context cleanly from raw game dict."""
        team_name = game['team'].lower().replace(' ', '_')
        game_date = game['date'].replace('-', '')
        return cls(
            team_name=team_name,
            game_date=game_date,
            file_name=f"{team_name}_{game_date}.mp4",
            field=field_configs[game['field']],
            is_home=game['is_home'],
            datetime=datetime.fromisoformat(game["datetime"])
        )

    def goal_file_name(self, score: int) -> str:
        return f"goal_{score}_{self.team_name}_{self.game_date}.mp4"

    def clip_folder_name(self) -> str:
        return f"{self.team_name}_{self.game_date}_HL"

    def has_occurred(self) -> bool:
        return self.datetime <= datetime.now()