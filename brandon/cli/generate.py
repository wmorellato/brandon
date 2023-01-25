import os
import click
import logging

from brandon.spec import Parser
from brandon.schemas import Languages
from brandon.builders.project import Project
from brandon.builders.docs import Builder as DocsBuilder
from brandon.builders.summary import Builder as SummaryBuilder

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@click.group(name="generate", help="Generation of different parts of the project.")
def generate_group():
    """`generate` command group"""


@generate_group.command(
    name="project",
    help="Generate the project structure and the command line interface from the CLI specification file pointed by FILENAME.",
)
@click.argument("filename")
@click.option(
    "-f",
    "--overwrite",
    "overwrite",
    is_flag=True,
    default=False,
    help="If there is a project folder in the path pointed by `output-path` option, overwrites its contents.",
)
@click.option(
    "-l",
    "--language",
    "language",
    help="Overwrite the default output language, which is defined from the first language provided in the `languages` key.",
)
@click.option(
    "-o",
    "--output-path",
    "output_path",
    default=os.getcwd(),
    help="Set the output path for the project folder.",
)
def project(filename, overwrite, language, output_path):
    """Parses the cli.yaml file and generate the
    project."""
    try:
        app = Parser(filename).app
        if not language:
            language = app.languages[0]
            logger.warning(
                f"The `--language` option was not provided. Using `{language}` from the `cli.yml` file"
            )

        if not Languages.is_supported(language):
            raise Exception(
                f"Invalid language `{language}`. Check the documentation for supported languages."
            )

        Project(
            app=app,
            language=Languages(language),
            output_path=output_path,
            overwrite=overwrite,
        ).create()
    except Exception as e:
        raise click.ClickException(str(e))

    click.echo(
        f"Project folder for `{app.name}` created successfully in `{output_path}`"
    )


@generate_group.command(
    name="docs",
    help="Generate the project documentation using MkDocs from the CLI specification file pointed by FILENAME.",
)
@click.argument("filename")
@click.option(
    "-o",
    "--output-path",
    "output_path",
    default=os.getcwd(),
    help="Set the output path for the documentation.",
)
def docs(filename, output_path):
    """Parses the cli.yaml file and generate the
    documentation.
    """
    try:
        app = Parser(filename).app
        DocsBuilder(app=app, output_path=output_path).build()
    except Exception as e:
        logger.error("Error", exc_info=True)
        raise click.ClickException(str(e))

    click.echo(
        f"Documentation folder for `{app.name}` created successfully in `{output_path}`"
    )


@generate_group.command(
    name="summary",
    help="Generate a summary of the command line interface, to be used somewhere else, from the CLI specification file pointed by FILENAME.",
)
@click.argument("filename")
def summary(filename):
    """Generate a summary of the command line interface,
    tobe used somewhere else, from the CLI specification
    file pointed by FILENAME.
    """
    try:
        app = Parser(filename).app
        click.echo(SummaryBuilder(app=app).build())
    except Exception as e:
        raise click.ClickException(str(e))
