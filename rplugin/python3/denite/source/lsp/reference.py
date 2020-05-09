import os
import site

from denite.util import Candidate, Nvim

path_to_lsp_module = os.path.abspath(os.path.dirname(__file__))
site.addsitedir(path_to_lsp_module)

from position import LspPosition  # isort:skip # noqa
from response import LspResponseEntry  # isort:skip # noqa


class LspReference:
    def __init__(self, vim: Nvim, response_entry: LspResponseEntry) -> None:
        self._vim = vim
        self._response_entry = response_entry
        self._validate()

    def _validate(self) -> None:
        if not ("uri" in self._response_entry):
            raise ValueError("Can not parse {self._response_entry} as {__name__}")

    @property
    def description(self) -> str:
        return "{} [{}:{}] > {}".format(
            self.relative_file_path,
            self.position.line,
            self.position.column,
            self.content_line,
        )

    @property
    def content_line(self) -> str:
        return self._vim.lua._lsp.read_file_line(self.file_path, self.position.line)

    @property
    def position(self) -> LspPosition:
        return LspPosition(self._response_entry["range"]["start"])

    @property
    def file_path(self):
        uri = self._response_entry["uri"]
        return self._vim.lua._lsp.uri_to_file_path(uri)

    @property
    def relative_file_path(self) -> str:
        working_directory = self._vim.call("getcwd")

        if self.file_path.startswith(working_directory):
            relative_start_index = len(working_directory) + 1
            return self.file_path[relative_start_index:]

        else:
            return self.file_path

    @property
    def as_candidate(self) -> Candidate:
        return {
            "word": self.description,
            "action__text": self.content_line,
            "action__path": self.file_path,
            "action__line": self.position.line,
            "action__col": self.position.column,
        }
