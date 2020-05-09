class HighlightLink:
    def __init__(
        self, name: str, parent_group: str, target_group: str, pattern: str
    ) -> None:
        self.name = name
        self.parent_group = parent_group
        self.target_group = target_group
        self.pattern = pattern

    @property
    def group(self):
        return f"{self.parent_group}_{self.name}"

    @property
    def syntax_match_command(self) -> str:
        return "syntax match {} /{}/ contained containedin={}".format(
            self.group, self.pattern, self.parent_group
        )

    @property
    def highlight_link_command(self):
        return f"highlight default link {self.group} {self.target_group}"
