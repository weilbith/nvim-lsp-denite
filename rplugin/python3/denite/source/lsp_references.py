import os
import site
from typing import List

from denite.util import Candidate, Nvim, UserContext

site.addsitedir(os.path.abspath(os.path.dirname(__file__) + os.path.sep + "lsp"))

from response import LspResponse  # isort:skip # noqa
from reference import LspReference  # isort:skip # noqa
from source import LspSource  # isort:skip # noqa
from highlighting import HighlightLink  # isort:skip # noqa


class Source(LspSource):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.name = "lsp_references"

    def on_init(self, context: UserContext) -> None:
        super().on_init(context)
        word = self._get_word_under_cursor()
        self.vim.out_write(f"{word}\n")
        self.highlight_links.extend(
            [
                HighlightLink("Position", self.syntax_name, "Comment", r"\[.*\]"),
                HighlightLink("Text", self.syntax_name, "String", r">\s.*$"),
                HighlightLink("Word", f"{self.syntax_name}_Text", "Operator", word),
            ]
        )

    def gather_candidates(self, context: UserContext) -> List[Candidate]:
        references = self._get_references()
        candidates = []

        for reference in references:
            candidates.append(reference.as_candidate)

        return candidates

    def _get_references(self) -> List[LspReference]:
        line, column = self.cursor_position
        response = LspResponse(
            self.vim.lua._lsp.get_references_for_position(
                self.buffer_number, line, column
            )
        )

        if response.is_error:
            self.vim.out_write(f"Error: {response.error_message}\n")
            return []

        else:
            return [
                LspReference(self.vim, response_entry)
                for response_entry in response.result
            ]

    def _get_word_under_cursor(self) -> str:
        return self.vim.call("expand", "<cword>")
