from typing import Any, Dict, List

from denite.base.source import Base
from denite.util import Candidate, Nvim, UserContext

LspResponse = List[Dict[str, Any]]
Reference = Dict[str, Any]

SYNTAX_LINKS = [
    {"name": "Position", "target_group": "Comment", "pattern": r"\[.*\]"},
    {"name": "Text", "target_group": "String", "pattern": r">\s.*$"},
]


class Source(Base):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.name = "lsp_references"
        self.kind = "file"

    def on_init(self, context: UserContext) -> None:
        self.vim.exec_lua("_lsp = require('nvim_lsp_denite')")
        context["cursor_position"] = self.vim.current.window.cursor
        context["buffer_number"] = self.vim.current.buffer.number

    def highlight(self) -> None:
        for syntax_link in SYNTAX_LINKS:
            name, target_group, pattern = syntax_link.values()
            group = f"{self.syntax_name}_{name}"

            self.vim.command(
                f"syntax match {group} /{pattern}/ contained containedin={self.syntax_name}"
            )
            self.vim.command(f"highlight default link {group} {target_group}")

    def gather_candidates(self, context: UserContext) -> List[Candidate]:
        references = self._get_references(
            context["buffer_number"], context["cursor_position"]
        )
        candidates = []

        for reference in references:
            candidates.append(self._reference_to_candidate(reference))

        return candidates

    def _get_references(self, buffer_number: int, cursor_position) -> List[Reference]:
        line, character = cursor_position
        response = self.vim.lua._lsp.get_references_for_position(
            buffer_number, line, character
        )

        if _response_is_error(response):
            self.vim.out_write(f"{_get_error_message(response)}\n")
            return []

        elif len(response) > 0:
            return response[0].get("result", [])

        else:
            return []

    def _reference_to_candidate(self, reference: Reference) -> Candidate:
        path = self.vim.lua._lsp.uri_to_filename(reference["uri"])
        location = reference["range"]["start"]
        line = location["line"] + 1
        character = location["character"] + 1
        text = self.vim.lua._lsp.read_file_line(path, line)

        return {
            "word": f"{path} [{line}:{character}] > {text}",
            "action__text": text,
            "action__path": path,
            "action__line": line,
            "action__col": character,
        }


def _response_is_error(response: LspResponse) -> bool:
    return len(response) == 1 and "error" in response[0]


def _get_error_message(response: LspResponse) -> str:
    return response[0].get("error", {}).get("message", "LSP response error")
