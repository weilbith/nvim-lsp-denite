local vim = vim
local lsp = require "vim.lsp"

local M = {}

local function lsp_client_available(buffer_number)
    return next(lsp.buf_get_clients(buffer_number)) ~= nil
end

function M.get_symbols_for_buffer(buffer_number, method)
    if not lsp_client_available(buffer_number) then
        return {}
    end

    local parameter = {textDocument = {uri = vim.uri_from_bufnr(buffer_number)}}
    local response = lsp.buf_request_sync(buffer_number, method, parameter)

    if response ~= nil then
        return response
    else
        return {}
    end
end

function M.uri_to_filename(uri)
    return vim.uri_to_fname(uri)
end

return M
