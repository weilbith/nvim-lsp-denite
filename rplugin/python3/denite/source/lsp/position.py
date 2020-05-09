from typing import Dict


class LspPosition:
    def __init__(self, start_range: Dict[str, int]) -> None:
        self._range = start_range
        self._validate()

    def _validate(self) -> None:
        if not ("line" in self._range and "character" in self._range):
            raise ValueError("Invalid range object for position!")

    @property
    def line(self) -> int:
        return int(self._range["line"]) + 1

    @property
    def column(self) -> int:
        return int(self._range["character"]) + 1
