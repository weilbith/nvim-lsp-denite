from typing import Any, Dict, List, Optional

LspResponseEntry = Dict[str, Any]


class LspResponse:
    def __init__(self, response: List[LspResponseEntry]) -> None:
        self._response = response

    @property
    def result(self) -> List[LspResponseEntry]:
        if len(self._response) > 0:
            return self._response[0].get("result", [])

        else:
            return []

    @property
    def is_error(self):
        return len(self._response) == 1 and "error" in self._response[0]

    @property
    def error_message(self) -> Optional[str]:
        if self.is_error:
            error = self._response[0].get("error", {})
            return error.get("message", None)
        else:
            return None
