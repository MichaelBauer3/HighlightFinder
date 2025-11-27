class ScoreValidator:

    def __init__(self, required_stable: int = 3):
        self.valid_after_frames = required_stable
        self.current_score = -1
        self.last_valid_score = -1
        self.frames_stable = 0

    def validate_score(self, current_frame_score: int) -> bool:

        if not self._is_valid_change(current_frame_score):
            self.current_score = -1
            self.frames_stable = 0
            return False

        if current_frame_score == self.current_score:
            self.frames_stable += 1
        else:
            self.current_score = current_frame_score
            self.frames_stable = 1

        if (self.frames_stable >= self.valid_after_frames and
            self.current_score != -1 and
            self.current_score != self.last_valid_score):

            self.last_valid_score = self.current_score
            return True

        return False

    def get_last_valid_score(self):
        return self.last_valid_score

    def _is_valid_change(self, current_frame_score: int) -> bool:

        if current_frame_score == self.last_valid_score:
            return True

        elif current_frame_score == (self.last_valid_score + 1):
            return True

        return False

