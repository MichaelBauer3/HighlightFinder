class ScoreValidator:

    def __init__(self, required_stable: int = 3):
        self.required_stable = required_stable
        self.last_valid_score = 0
        self.current_candidate = None
        self.frames_stable = 0

    def validate_score(self, frame_score: int) -> bool:

        if frame_score <= self.last_valid_score:
            self._reset_candidate()
            return False

        if frame_score != self.current_candidate:
            self.current_candidate = frame_score
            self.frames_stable = 1
        else:
            self.frames_stable += 1

        if self.frames_stable >= self.required_stable:
            self.last_valid_score = self.current_candidate
            self._reset_candidate()
            return True

        return False

    def get_last_valid_score(self):
        return self.last_valid_score

    def _reset_candidate(self):
        self.current_candidate = None
        self.frames_stable = 0