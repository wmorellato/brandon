import click
import logging

from brandon.spec import Parser
from brandon.cli.generate import generate_group

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@click.group()
def cli():
    """CLI entry point"""


@cli.command(name="version", help="Show the version and exit.")
def version():
    """`version` command handler"""
    try:
        app = Parser("./cli.yml").app
        click.echo(app.version)
    except Exception as e:
        raise click.ClickException(str(e))


cli.add_command(generate_group)


if __name__ == "__main__":
    cli()
