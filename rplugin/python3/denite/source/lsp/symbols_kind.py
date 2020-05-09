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


class LspSymbolsKind:
    def __init__(self, identifier: int) -> None:
        self._identifier = identifier

    @property
    def name(self):
        if self._identifier < len(SYMBOL_ID_TO_NAME):
            return SYMBOL_ID_TO_NAME[self._identifier - 1]

        else:
            return "unknown"
