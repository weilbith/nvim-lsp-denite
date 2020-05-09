local vim = vim
local api = vim.api
local lsp = require "vim.lsp"

local M = {}

local function lsp_client_available(buffer_number)
    return next(lsp.buf_get_clients(buffer_number)) ~= nil
end

local function make_document_parameter(buffer_number)
    return {uri = vim.uri_from_bufnr(buffer_number)}
end

local function make_document_symbols_parameter(buffer_number)
    return {textDocument = make_document_parameter(buffer_number)}
end

local function make_workspace_symbols_parameter(buffer_number)
    return {query = ""}
end

local function make_references_parameter(buffer_number, line, character)
    return {
        textDocument = make_document_parameter(buffer_number),
        position = {line = line - 1, character = character},
        context = {includeDeclaration = true}
    }
end

local function parse_response(response)
    if response ~= nil then
        return response
    else
        return {}
    end
end

function M.get_document_symbols(buffer_number)
    if not lsp_client_available(buffer_number) then
        return {}
    end

    local parameter = make_document_symbols_parameter(buffer_number)
    local response = lsp.buf_request_sync(buffer_number, "textDocument/documentSymbol", parameter)
    return parse_response(response)
end

function M.get_workspace_symbols(buffer_number)
    if not lsp_client_available(buffer_number) then
        return {}
    end

    local parameter = make_workspace_symbols_parameter(buffer_number)
    local response = lsp.buf_request_sync(buffer_number, "workspace/symbol", parameter)
    return parse_response(response)
end

function M.get_references_for_position(buffer_number, line, character)
    if not lsp_client_available(buffer_number) then
        return {}
    end

    local parameter = make_references_parameter(buffer_number, line, character)
    local response = lsp.buf_request_sync(buffer_number, "textDocument/references", parameter)
    return parse_response(response)
end

function M.uri_to_file_path(uri)
    return vim.uri_to_fname(uri)
end

function M.uri_from_buffer_number(buffer_number)
    return vim.uri_from_bufnr(buffer_number)
end

function M.read_file_line(file_path, line)
    local lines = api.nvim_call_function("readfile", {file_path, "", line})
    return lines[line]
end

return M
