# NVim LSP Denite

This plugin provides additional sources for the
[denite.nvim](https://github.com/Shougo/denite.nvim) plugin in relation to
language servers. Be aware that this only works with the native language server
protocol support by [NeoVim](https://neovim.io/).

## Installation

Install the plugin with your favorite manager tool. Here is an example using
[dein.vim](https://github.com/Shougo/dein.vim):

```vim
call dein#add('weilbith/nvim-lsp-denite')
```

Please make sure that you have also installed the following plugins:

- [denite.nvim](https://github.com/Shougo/denite.nvim) [required]
- [nvim-lsp](https://github.com/neovim/nvim-lsp) [optional]

## Usage

The provided sources are directly available without any configuration. All
sources have the prefix `lsp_*`. Be aware that buffers without an attached LSP
client will produce empty candidate lists only.

An good example is the attractive alternative to the native `outline` source of
_denite.nvim_ that queries the symbols of the current buffer by the language
server:

```vim
:Denite lsp_symbols
```
