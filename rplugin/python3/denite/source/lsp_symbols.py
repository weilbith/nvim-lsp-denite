from functools import reduce
from typing import Any, Dict, List, Tuple

from denite.base.source import Base
from denite.util import Candidate, Nvim, UserContext

LspResponse = List[Dict[str, Any]]
Symbol = Dict[str, Any]
DocumentSymbol = Symbol
SymbolInformation = Symbol
Position = Tuple[int, int]

SYMBOL_ID_TO_NAME = [
    "File",
    "Module",
    "Namespace",
    "Package",
    "Class",
    "Method",
    "Property",
    "Field",
    "Constructor",
    "Enum",
    "Interface",
    "Function",
    "Variable",
    "Constant",
    "String",
    "Number",
    "Boolean",
    "Array",
    "Object",
    "Key",
    "Null",
    "EnumMember",
    "Struct",
    "Event",
    "Operator",
    "TypeParameter",
]

SYNTAX_LINKS = [
    {"name": "Kind", "target_group": "Special", "pattern": r"\[.*\]"},
    {"name": "Origin", "target_group": "Comment", "pattern": r"(.*)"},
]


class Source(Base):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.name = "lsp_symbols"
        self.kind = "file"
        self.buffe_number = None

    def on_init(self, context: UserContext) -> None:
        self.vim.exec_lua("_lsp = require('nvim_lsp_denite')")
        self.buffer_number = self.vim.current.buffer.number
        self.lsp_method = _get_lsp_method(context)

    def highlight(self) -> None:
        for syntax_link in SYNTAX_LINKS:
            name, target_group, pattern = syntax_link.values()
            group = f"{self.syntax_name}_{name}"

            self.vim.command(
                f"syntax match {group} /{pattern}/ contained containedin={self.syntax_name}"
            )
            self.vim.command(f"highlight default link {group} {target_group}")

    def gather_candidates(self, context: UserContext) -> List[Candidate]:
        symbols = self._get_symbols(self.buffer_number, self.lsp_method)
        candidates: List[Candidate] = []

        for symbol in symbols:
            candidates.extend(self._symbol_to_candidates(symbol))

        return candidates

    def _get_symbols(self, buffer_number: int, lsp_method: str) -> List[Symbol]:
        response = self.vim.lua._lsp.get_symbols_for_buffer(buffer_number, lsp_method)

        if _response_is_error(response):
            return []

        elif len(response) > 0:
            return response[0].get("result", [])

        else:
            return []

    def _symbol_to_candidates(
        self, symbol: Symbol, parents: List[str] = []
    ) -> List[Candidate]:
        candidates = [self._symbol_to_candidate(symbol, parents)]

        if _symbol_is_document_symbol(symbol):
            parents.append(_get_symbol_name(symbol))

            for child_symbol in symbol.get("children", []):
                candidates.extend(self._symbol_to_candidates(child_symbol, parents))

        return candidates

    def _symbol_to_candidate(self, symbol: Symbol, parents: List[str]) -> Candidate:
        position = _get_symbol_position(symbol)

        return {
            "word": _get_symbol_description(symbol, parents),
            "action__text": _get_symbol_description(symbol, parents),
            "action__pattern": _get_symbol_name(symbol),
            "action__path": self._get_symbol_file_path(symbol),
            "action__line": position[0],
            "action__col": position[1],
        }

    def _get_symbol_file_path(self, symbol: Symbol) -> str:
        uri = "undefined"

        if _symbol_is_symbol_information(symbol):
            uri = symbol["location"]["uri"]

        if _symbol_is_document_symbol(symbol):
            uri = self.vim.lua._lsp.uri_from_buffer_number(self.buffer_number)

        return self.vim.lua._lsp.uri_to_file_path(uri)


def _get_lsp_method(context: UserContext) -> str:
    arguments = context["args"]

    if len(arguments) > 0:
        return arguments[0]
    else:
        return "textDocument/documentSymbol"


def _response_is_error(response: LspResponse) -> bool:
    return len(response) == 1 and "error" in response[0]


def _get_error_message(response: LspResponse) -> str:
    return response[0].get("error", {}).get("message", "LSP response error")


def _get_symbol_name(symbol: Symbol) -> str:
    return symbol["name"]


def _get_symbol_description(symbol: Symbol, parents: List[str]) -> str:
    name = _get_symbol_name(symbol)
    kind = _get_symbol_kind(symbol)
    origin = reduce((lambda x, y: f"{x}.{y}"), parents, "")[1:]

    return f"{name} - [{kind}] " + ("" if not origin else f"({origin})")


def _symbol_is_document_symbol(symbol: Symbol) -> bool:
    return "range" in symbol and "selectionRange" in symbol


def _symbol_is_symbol_information(symbol: Symbol) -> bool:
    return "location" in symbol


def _get_symbol_kind(symbol: Symbol) -> str:
    kind_id = symbol["kind"]

    if kind_id < len(SYMBOL_ID_TO_NAME):
        return SYMBOL_ID_TO_NAME[kind_id - 1]
    else:
        return "unknown"


def _get_symbol_position(symbol: Symbol) -> Position:
    range_start: Dict[str, int] = {"line": 0, "character": 0}

    if _symbol_is_document_symbol(symbol):
        range_start = symbol["range"]["start"]

    if _symbol_is_symbol_information(symbol):
        range_start = symbol["location"]["range"]["start"]

    return (range_start["line"] + 1, range_start["character"] + 1)
