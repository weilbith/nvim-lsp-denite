from typing import Any, Dict, List

from denite.base.source import Base
from denite.util import Candidate, Nvim, UserContext

LspResponse = List[Dict[str, Any]]
Symbol = Dict[str, Any]

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
]


class Source(Base):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.name = "lsp_symbols"
        self.kind = "file"

    def on_init(self, context: UserContext) -> None:
        self.vim.exec_lua("_lsp = require('nvim_lsp_denite')")
        context["buffer_number"] = self.vim.current.buffer.number
        context["lsp_method"] = _get_lsp_method(context)

    def highlight(self) -> None:
        for syntax_link in SYNTAX_LINKS:
            name, target_group, pattern = syntax_link.values()
            group = f"{self.syntax_name}_{name}"

            self.vim.command(
                f"syntax match {group} /{pattern}/ contained containedin={self.syntax_name}"
            )
            self.vim.command(f"highlight default link {group} {target_group}")

    def gather_candidates(self, context: UserContext) -> List[Candidate]:
        symbols = self._get_symbols(context["buffer_number"], context["lsp_method"])
        candidates = []

        for symbol in symbols:
            candidates.append(self._symbol_to_candidate(symbol))

        return candidates

    def _get_symbols(self, buffer_number: int, lsp_method: str) -> List[Symbol]:
        response = self.vim.lua._lsp.get_symbols_for_buffer(buffer_number, lsp_method)

        if _response_is_error(response):
            self.vim.out_write(f"{_get_error_message(response)}\n")
            return []

        elif len(response) > 0:
            return response[0].get("result", [])

        else:
            return []

    def _symbol_to_candidate(self, symbol: Symbol) -> Candidate:
        name = symbol["name"]
        kind = _get_kind_name(symbol["kind"])
        description = f"{name} - [{kind}]"
        location = symbol["location"]
        path = self.vim.lua._lsp.uri_to_filename(location["uri"])
        position = location["range"]["start"]

        return {
            "word": description,
            "action__text": description,
            "action__pattern": name,
            "action__path": path,
            "action__line": position["line"] + 1,
            "action__col": position["character"] + 1,
        }


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


def _get_kind_name(kind_id: int) -> str:
    if kind_id < len(SYMBOL_ID_TO_NAME):
        return SYMBOL_ID_TO_NAME[kind_id - 1]
    else:
        return "unknown"
