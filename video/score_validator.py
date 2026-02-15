class ScoreValidator:
    def __init__(self, required_stable: int = 3):
        self.required_stable = required_stable
        self.max_increment = 1
        self.last_valid_score = -1
        self.current_candidate = None
        self.frames_stable = 0
        self.initialized = False

    def validate_score(self, frame_score: int) -> bool:

        if not self.initialized:
            if frame_score == 0:
                if self.current_candidate != 0:
                    self.current_candidate = 0
                    self.frames_stable = 1
                else:
                    self.frames_stable += 1

                if self.frames_stable >= self.required_stable:
                    self.last_valid_score = 0
                    self.initialized = True
                    self._reset_candidate()
            else:
                self._reset_candidate()
            return False

        if frame_score == self.last_valid_score:
            self._reset_candidate()
            return False

        score_increase = frame_score - self.last_valid_score

        if score_increase == self.max_increment:
            if frame_score != self.current_candidate:
                self.current_candidate = frame_score
                self.frames_stable = 1
            else:
                self.frames_stable += 1

            if self.frames_stable >= self.required_stable:
                self.last_valid_score = self.current_candidate
                self._reset_candidate()
                return True
        else:
            self._reset_candidate()

        return False

    def _reset_candidate(self):
        self.current_candidate = None
        self.frames_stable = 0