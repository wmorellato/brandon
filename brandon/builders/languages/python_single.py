import os
import re
import logging
import keyword

from brandon.md_utils import sandwich
from brandon.builders.languages.python import Module, Decorator

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Builder:
    """Builder for single-file Python scripts.
    """

    def __init__(self, app, output_path) -> None:
        self.app = app
        self.output_path = output_path

    def build(self):
        self._create_module()

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
    
    def _create_module(self):
        script_mod = Module(self.app.exec, path=self.output_path, imports=["click"])

        # group modules
        for g in self.app.cli.groups:
            group_def = Decorator(
                name="click.group",
                kwargs={"name": f'"{g.name}"', "help": f'"{g.description}"'},
            )

            script_mod.add_function(
                name=f"{g.name}_group",
                comment=f"`{g.name}` command group",
                decorators=[group_def],
            )

            for c in g.commands:
                decorators = self._create_grouped_command_decs(g, c)
                params = self._create_command_params(c)
                script_mod.add_function(
                    name=f"{c.name}",
                    comment=f"`{c.name}` command handler",
                    decorators=decorators,
                    params=params,
                )

        main_group_dec = Decorator("click.group")
        script_mod.add_function(
            name="cli", comment="CLI entry point", decorators=[main_group_dec]
        )

        # ungrouped commands
        for c in self.app.cli.commands:
            decorators = self._create_ungrouped_command_decs(c)
            params = self._create_command_params(c)
            script_mod.add_function(
                name=f"{c.name}",
                comment=f"`{c.name}` command handler",
                decorators=decorators,
                params=params,
            )

        for g in self.app.cli.groups:
            script_mod.add_expr(f"cli.add_command({g.name}_group)")

        script_mod.add_expr(os.linesep)
        script_mod.add_main(function_name="cli")
        script_mod.write()
