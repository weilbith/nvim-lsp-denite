import os
import site
from typing import Dict, List

from denite.util import Candidate, Nvim, UserContext

site.addsitedir(os.path.abspath(os.path.dirname(__file__) + os.path.sep + "lsp"))

from response import LspResponse  # isort:skip # noqa
from symbols import LspSymbol  # isort:skip # noqa
from symbols_scope import LspSymbolsScope  # isort:skip # noqa
from source import LspSource  # isort:skip # noqa
from highlighting import HighlightLink  # isort:skip # noqa


class Source(LspSource):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.name = "lsp_symbols"

    def on_init(self, context: UserContext) -> None:
        super().on_init(context)
        self.highlight_links.extend(
            [
                HighlightLink("Kind", self.syntax_name, "Special", r"\[.*\]"),
                HighlightLink("Origin", self.syntax_name, "Comment", r"(.*)"),
            ]
        )

    def gather_candidates(self, context: UserContext) -> List[Candidate]:
        self.context = context
        symbols = self._get_symbols()
        candidates: List[Candidate] = []

        for symbol in symbols:
            candidates.extend(self._get_candidates_hierarchically(symbol))

        return candidates

    def _get_symbols(self) -> List[LspSymbol]:
        response = self._query_language_server()

        if response.is_error:
            self.vim.out_write(f"Error: {response.error_message}\n")
            return []

        else:
            return [
                LspSymbol(self.vim, response_entry, self.buffer_number)
                for response_entry in response.result
            ]

    def _query_language_server(self) -> LspResponse:
        plain_response: Dict = {}

        if self.scope is LspSymbolsScope.Document:
            plain_response = self.vim.lua._lsp.get_document_symbols(self.buffer_number)

        if self.scope is LspSymbolsScope.Workspace:
            plain_response = self.vim.lua._lsp.get_workspace_symbols(self.buffer_number)

        return LspResponse(plain_response)

    def _get_candidates_hierarchically(
        self, symbol: LspSymbol, parents: List[str] = []
    ) -> List[Candidate]:
        candidates = [symbol.as_candidate]

        parents_for_child = parents.copy()
        parents_for_child.append(symbol.name)

        for child in symbol.children:
            child_symbol = LspSymbol(
                self.vim, child, self.buffer_number, parents_for_child
            )
            candidates.extend(
                self._get_candidates_hierarchically(child_symbol, parents_for_child)
            )

        return candidates

    @property
    def scope(self) -> LspSymbolsScope:
        arguments = self.context["args"]
        scope_argument = arguments[0] if len(arguments) > 0 else None

        try:
            return LspSymbolsScope(scope_argument)

        except Exception:
            return LspSymbolsScope.Document
