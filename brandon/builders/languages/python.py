import os
import re
import logging
import keyword

from brandon.md_utils import sandwich

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Module:
    def __init__(self, name, path, imports=[]) -> None:
        self.name = name
        self.filepath = os.path.join(path, f"{name}.py")
        self.imports = imports
        self.lines = []

        self._write_imports()

    def _write_imports(self):
        for i in self.imports:
            if "." in i:
                parts = i.split(".")
                self.add_expr(f"from {'.'.join(parts[:-1])} import {parts[-1]}")
                continue

            self.add_expr(f"import {i}")
        self.add_expr(os.linesep)

    def add_expr(self, line, level=0):
        self.lines.append("    " * level + line)

    def add_enum(self, enum):
        fmt_name = re.sub("[^A-Za-z]", "", enum.name.title())
        if not fmt_name.isidentifier() or keyword.iskeyword(fmt_name):
            fmt_name = f"_{fmt_name}"

        self.add_expr(f"class {fmt_name}(Enum):")
        if enum.description:
            self.add_expr(f'"""{enum.description}"""', level=1)

        for k, v in enum.items.items():
            guard = '"' if type(v) == str else ""
            fmt_item_name = re.sub("[^A-Za-z_]", "", k).upper()
            self.add_expr(f"{fmt_item_name} = {sandwich(v, guard)}", level=1)
        self.add_expr(os.linesep)

    def add_function(self, name, comment, params=[], decorators=[]):
        fmt_name = re.sub("[^A-Za-z_]", "", name.replace("-", "_")).lower()
        if not fmt_name.isidentifier() or keyword.iskeyword(fmt_name):
            fmt_name = f"_{fmt_name}"

        for d in decorators:
            self.add_expr(d.expression)

        self.add_expr(f"def {fmt_name}({', '.join(params)}):")
        self.add_expr(f'"""{comment}"""', level=1)
        self.add_expr(os.linesep)

    def add_main(self, function_name="main"):
        self.add_expr('if __name__ == "__main__":')
        self.add_expr(f"{function_name}()", level=1)
        self.add_expr("")

    def write(self):
        with open(self.filepath, "w") as fp:
            fp.write(os.linesep.join(self.lines))
            fp.write(os.linesep)


class Decorator:
    def __init__(self, name, no_params=False, args=[], kwargs={}) -> None:
        self.name = name
        self.no_params = no_params
        self.args = args
        self.kwargs = kwargs

    @property
    def expression(self):
        if self.no_params:
            return f"@{self.name}"

        if len(self.kwargs) == 0 and len(self.args) == 0:
            return f"@{self.name}()"

        if len(self.kwargs) == 0:
            return f'@{self.name}({", ".join(self.args)})'

        if len(self.args) == 0:
            return (
                f'@{self.name}({", ".join(f"{k}={v}" for k,v in self.kwargs.items())})'
            )

        return f'@{self.name}({", ".join(self.args)}, {", ".join(f"{k}={v}" for k,v in self.kwargs.items())})'


class Builder:
    """Builder for Python projects. The project structure
    is:

    """

    def __init__(self, app, output_path) -> None:
        self.app = app
        self.project_root = os.path.join(output_path, f"{app.exec}-{app.version}")
        self.source_root = os.path.join(self.project_root, f"{app.exec}")

    def build(self):
        self._create_directories()
        self._create_modules()
        self._create_readme()
        self._create_toml()

    def _create_directories(self):
        os.makedirs(self.project_root, exist_ok=True)
        os.makedirs(os.path.join(self.source_root, "cli"), exist_ok=True)
        os.makedirs(os.path.join(self.project_root, "tests"), exist_ok=True)

    def _create_grouped_command_decs(self, group, command):
        decorators = []
        decorators.append(
            Decorator(
                name=f"{group.name}_group.command",
                kwargs={
                    "name": f'"{command.name}"',
                    "help": f'"{command.description}"',
                },
            )
        )

        for a in command.arguments:
            decorators.append(Decorator(name="click.argument", args=[f'"{a.name}"']))

        for o in command.options:
            if o.short:
                decorators.append(
                    Decorator(
                        name="click.option",
                        args=[f'"-{o.short}"', f'"--{o.name}"', f'"{o.name}"'],
                        kwargs={"help": f'"{o.description}"'},
                    )
                )
            else:
                decorators.append(
                    Decorator(
                        name="click.option",
                        args=[f'"--{o.name}"', f'"{o.name}"'],
                        kwargs={"help": f'"{o.description}"'},
                    )
                )

        return decorators

    def _create_ungrouped_command_decs(self, command):
        decorators = []
        decorators.append(
            Decorator(
                name="cli.command",
                kwargs={
                    "name": f'"{command.name}"',
                    "help": f'"{command.description}"',
                },
            )
        )

        for a in command.arguments:
            decorators.append(Decorator(name="click.argument", args=[f'"{a.name}"']))

        for o in command.options:
            if o.short:
                decorators.append(
                    Decorator(
                        name="click.option",
                        args=[f'"-{o.short}"', f'"--{o.name}"', f'"{o.name}"'],
                        kwargs={"help": f'"{o.description}"'},
                    )
                )
            else:
                decorators.append(
                    Decorator(
                        name="click.option",
                        args=[f'"--{o.name}"', f'"{o.name}"'],
                        kwargs={"help": f'"{o.description}"'},
                    )
                )

        return decorators

    def _create_command_params(self, command):
        params = []

        for a in command.arguments:
            params.append(a.name)

        for o in command.options:
            params.append(o.name)

        return params

    def _create_modules(self):
        cli_dir = os.path.join(self.source_root, "cli")
        Module("__init__", path=self.source_root).write()
        Module("__init__", path=cli_dir).write()

        # group modules
        for g in self.app.cli.groups:
            group_def = Decorator(
                name="click.group",
                kwargs={"name": f'"{g.name}"', "help": f'"{g.description}"'},
            )
            group_mod = Module(name=g.name, path=cli_dir, imports=["click"])
            group_mod.add_function(
                name=f"{g.name}_group",
                comment=f"`{g.name}` command group",
                decorators=[group_def],
            )

            for c in g.commands:
                decorators = self._create_grouped_command_decs(g, c)
                params = self._create_command_params(c)
                group_mod.add_function(
                    name=f"{c.name}",
                    comment=f"`{c.name}` command handler",
                    decorators=decorators,
                    params=params,
                )
            group_mod.write()

        # main module
        group_imports = [
            f"{self.app.exec}.cli.{g.name}.{g.name}_group" for g in self.app.cli.groups
        ]
        main_mod = Module(
            name="main", path=self.source_root, imports=["click"] + group_imports
        )
        main_group_dec = Decorator("click.group")
        main_mod.add_function(
            name="cli", comment="CLI entry point", decorators=[main_group_dec]
        )

        # ungrouped commands
        for c in self.app.cli.commands:
            decorators = self._create_ungrouped_command_decs(c)
            params = self._create_command_params(c)
            main_mod.add_function(
                name=f"{c.name}",
                comment=f"`{c.name}` command handler",
                decorators=decorators,
                params=params,
            )

        for g in self.app.cli.groups:
            main_mod.add_expr(f"cli.add_command({g.name}_group)")

        main_mod.add_expr(os.linesep)
        main_mod.add_main(function_name="cli")
        main_mod.write()

        # schemas module
        schemas_mod = Module(
            name="schemas", path=self.source_root, imports=["enum.Enum"]
        )

        for e in self.app.schemas.enums:
            schemas_mod.add_enum(e)
        schemas_mod.write()

    def _create_readme(self):
        with open(os.path.join(self.project_root, "README.md"), "w") as fp:
            fp.write(f"# {self.app.name}{os.linesep}")

    def _create_toml(self):
        lines = []

        lines.append("[tool.poetry]")
        lines.append(f'name = "{self.app.name}"')
        lines.append(f'version = "{self.app.version}"')
        lines.append(f'description = "{self.app.description}"')

        if self.app.authors:
            lines.append(f"authors = [{self.app.authors}]")

        lines.append("")
        lines.append("[tool.poetry.scripts]")
        lines.append(f'{self.app.exec} = "{self.app.exec}.main:cli"')

        lines.append("")
        lines.append("[tool.poetry.dependencies]")
        lines.append('click = "8.1.3"')
        lines.append("")

        with open(os.path.join(self.project_root, "pyproject.toml"), "w") as fp:
            fp.write(os.linesep.join(lines))

    def _create_cli_yml(self):
        pass
