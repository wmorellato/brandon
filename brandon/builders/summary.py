import os


class Builder:
    """Create a short summary of the specified application."""

    def __init__(self, app) -> None:
        self.app = app
        self.lines = []

    def build(self) -> str:
        self._create_summary()
        return os.linesep.join(self.lines)

    def _create_summary(self):
        self._add_line(f"{self.app.name} - {self.app.description}", True)
        self._add_line(f"Usage:\n    {self.app.exec} [command]", True)

        self._add_line(f"Commands:")

        command_lines = []
        max_width = 0
        for g in self.app.cli.groups:
            group_line = (
                f"    {self.app.exec} {g.name} {'|'.join(c.name for c in g.commands)}"
            )
            max_width = max(max_width, len(group_line))
            command_lines.append([group_line, g.description])

        for c in self.app.cli.commands:
            command_line = f"    {self.app.exec} {c.name}"
            max_width = max(max_width, len(command_line))
            command_lines.append([command_line, c.description])

        for c in command_lines:
            self._add_line(f"{c[0]:{max_width+5}}{c[1]}")

        self._add_line("")
        self._add_line(f"Authors:")
        for a in self.app.authors:
            if not a.email:
                self._add_line(f"    {a.name}")
            else:
                self._add_line(f"    {a.name} <{a.email}>")

    def _add_line(self, text, double_nl=False):
        self.lines.append(text)
        if double_nl:
            self.lines.append("")
