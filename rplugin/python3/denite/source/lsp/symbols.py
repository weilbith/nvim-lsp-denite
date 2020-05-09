import os
import site
from functools import reduce
from sys import maxsize
from typing import List, Optional

from denite.util import Candidate, Nvim

site.addsitedir(os.path.abspath(os.path.dirname(__file__)))

from position import LspPosition  # isort:skip # noqa
from response import LspResponseEntry  # isort:skip # noqa
from symbols_kind import LspSymbolsKind  # isort:skip # noqa
from symbols_type import LspSymbolsType  # isort:skip # noqa


class LspSymbol:
    def __init__(
        self,
        vim: Nvim,
        response_entry: LspResponseEntry,
        buffer_number: int,
        parents: List[str] = [],
    ) -> None:
        self._vim = vim
        self._response_entry = response_entry
        self.buffer_number = buffer_number
        self.parents = parents
        self._validate()

    def _validate(self) -> None:
        if not ("name" in self._response_entry and "kind" in self._response_entry):
            raise ValueError("Can not parse {self._response_entry} as {__name__}")

    @property
    def name(self) -> str:
        return self._response_entry["name"]

    @property
    def kind(self) -> LspSymbolsKind:
        return LspSymbolsKind(self._response_entry.get("kind", maxsize))

    @property
    def type(self) -> LspSymbolsType:
        if "range" in self._response_entry:
            return LspSymbolsType.DocumentSymbol

        elif "location" in self._response_entry:
            return LspSymbolsType.SymbolInformation
        else:
            raise ValueError("Unsupported symbol type!")

    @property
    def origin(self) -> Optional[str]:
        if self.type is LspSymbolsType.DocumentSymbol:
            return reduce((lambda x, y: f"{x}.{y}"), self.parents, "")[1:]

        elif self.type is LspSymbolsType.SymbolInformation:
            return self._response_entry.get("containerName", None)

        else:
            return None

    @property
    def description(self):
        description = f"{self.name} - [{self.kind.name}]"

        if self.origin:
            description += f" ({self.origin})"

        return description

    @property
    def position(self) -> LspPosition:
        if self.type is LspSymbolsType.DocumentSymbol:
            return LspPosition(self._response_entry["range"]["start"])

        elif self.type is LspSymbolsType.SymbolInformation:
            return LspPosition(self._response_entry["location"]["range"]["start"])

        else:
            raise ValueError("Symbol is missing positional property!")

    @property
    def file_path(self) -> str:
        uri = "undefined"

        if self.type is LspSymbolsType.DocumentSymbol:
            uri = self._vim.lua._lsp.uri_from_buffer_number(self.buffer_number)

        elif self.type is LspSymbolsType.SymbolInformation:
            uri = self._response_entry["location"]["uri"]

        return self._vim.lua._lsp.uri_to_file_path(uri)

    @property
    def children(self) -> List[LspResponseEntry]:
        if self.type is LspSymbolsType.DocumentSymbol:
            return self._response_entry["children"]

        else:
            return []

    @property
    def as_candidate(self) -> Candidate:
        return {
            "word": self.description,
            "action__text": self.description,
            "action__pattern": self.name,
            "action__path": self.file_path,
            "action__line": self.position.line,
            "action__col": self.position.column,
        }
