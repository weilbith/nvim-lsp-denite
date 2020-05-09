import os
import site
from typing import List

from denite.base.source import Base
from denite.util import Nvim, UserContext

site.addsitedir(os.path.abspath(os.path.dirname(__file__)))

from highlighting import HighlightLink  # isort:skip # noqa


class LspSource(Base):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.kind = "file"
        self.highlight_links: List[HighlightLink] = []

    def on_init(self, context: UserContext) -> None:
        self.vim.exec_lua("_lsp = require('nvim_lsp_denite')")
        self.buffer_number = self.vim.current.buffer.number
        self.cursor_position = self.vim.current.window.cursor
        self.context = context

    def highlight(self) -> None:
        for link in self.highlight_links:
            self.vim.command(link.syntax_match_command)
            self.vim.command(link.highlight_link_command)
