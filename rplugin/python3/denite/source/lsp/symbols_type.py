from enum import Enum, unique


@unique
class LspSymbolsType(Enum):
    DocumentSymbol = "DocumentSymbol"
    SymbolInformation = "SymbolInformation"
