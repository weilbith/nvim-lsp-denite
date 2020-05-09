from enum import Enum, unique


@unique
class LspSymbolsScope(Enum):
    Document = "document"
    Workspace = "workspace"
