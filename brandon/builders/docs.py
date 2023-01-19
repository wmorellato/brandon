import os
import re
import yaml
import subprocess
from enum import Enum
from urllib.parse import urlparse
from materialx.emoji import twemoji, to_svg

from brandon.md_utils import (
    Document,
    Heading,
    Paragraph,
    Table,
    UnorderedList,
    Link,
    Command,
    sandwich,
)


class Icons(Enum):
    MAIL = ":material-mail:"
    GITHUB = ":material-github:"
    TWITTER = ":material-twitter:"
    LINKEDIN = ":material-linkedin:"
    DISCORD = ":simple-discord:"
    STACK = ":material-stack-overflow:"
    DEFAULT = ":material-web:"

    @classmethod
    def guess(cls, url: str):
        o = urlparse(url)
        for c in o.netloc.split("."):
            for site in cls:
                if c in site.value:
                    return site
        return cls.DEFAULT


class Builder:
    """Create mkdocs configuration file and necessary
    pages for the projects documentation.
    """

    def __init__(self, app, output_path: str) -> None:
        self.app = app
        self.output_path = os.path.join(output_path, f"{app.exec}-docs")
        self.pages_dir = os.path.join(self.output_path, "docs")
        self.reference_pages_dir = os.path.join(self.pages_dir, "reference")

    def build(self):
        self._create_directories()
        self._write_mkdocs_conf()
        self._write_pages()

        # building the site
        subprocess.run(["mkdocs", "build"], cwd=self.output_path)

    def _create_directories(self):
        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(self.pages_dir, exist_ok=True)

        # reference subfolder
        os.makedirs(self.reference_pages_dir, exist_ok=True)

        # subfolders for groups
        for g in self.app.cli.groups:
            os.mkdir(os.path.join(self.reference_pages_dir, g.name))

    def _write_mkdocs_conf(self):
        """Too much stuff going on here"""
        conf_file = os.path.join(self.output_path, "mkdocs.yml")

        nav = []
        nav.append({"Home": "index.md"})
        reference_page = []

        commands_section = {"Commands": []}
        for g in self.app.cli.groups:
            group = {g.name: []}
            for c in g.commands:
                group[g.name].append({c.name: f"reference/{g.name}/{c.name}.md"})
            commands_section["Commands"].append(group)

        for c in self.app.cli.commands:
            commands_section["Commands"].append({c.name: f"reference/{c.name}.md"})

        reference_page.append(commands_section)
        reference_page.append({"Schemas": [{"Enums": "reference/enums.md"}]})

        nav.append({"Reference": reference_page})

        with open(conf_file, "w") as fp:
            yaml.dump(
                {
                    "site_name": self.app.name,
                    "theme": {"name": "material", "features": ["navigation.instant"]},
                    "repo_url": self.app.url,
                    "nav": nav,
                    "markdown_extensions": [
                        "attr_list",
                        {
                            "pymdownx.emoji": {
                                "emoji_index": twemoji,
                                "emoji_generator": to_svg,
                            }
                        },
                        {"pymdownx.highlight": {"anchor_linenums": True}},
                        "pymdownx.inlinehilite",
                        "pymdownx.snippets",
                        "pymdownx.superfences",
                    ],
                },
                fp,
                sort_keys=False,
            )

    def _write_pages(self):
        self._write_index_page()

        for g in self.app.cli.groups:
            for c in g.commands:
                self._write_command_page(c, g.name)

        for c in self.app.cli.commands:
            self._write_command_page(c)

        if self.app.schemas:
            self._write_enums_page()

    def _author_list(self):
        for a in self.app.authors:
            parts = [
                a.name,
                ":",
                Link(Icons.MAIL.value, f"mailto:{a.email}").render(),
                Link(Icons.guess(a.url).value, a.url).render(),
            ]
            yield " ".join(parts)

    def _write_index_page(self):
        page_file = os.path.join(self.pages_dir, "index.md")

        with open(page_file, "w") as fp:
            doc = Document(self.app.name)
            doc.add(Paragraph(self.app.description))

            if self.app.authors:
                doc.add(Heading("Authors", level=1))
                doc.add(UnorderedList(self._author_list()))

            doc.write(fp)

    def _write_command_page(self, command, group=None):
        def args_rows(args):
            for a in args:
                desc = a.description if a.description else ""
                exmp = a.example if a.example else ""
                yield [sandwich(a.name, "`"), a.type.value, desc, exmp]

        def opts_rows(opts):
            for o in opts:
                desc = o.description if o.description else ""
                exmp = o.example if o.example else ""
                default = o.default if o.default else ""
                yield [sandwich(o.name, "`"), o.type.value, desc, default, exmp]

        if group is not None:
            page_file = os.path.join(
                self.reference_pages_dir, group, f"{command.name}.md"
            )
        else:
            page_file = os.path.join(self.reference_pages_dir, f"{command.name}.md")
        cmd_parts = [self.app.exec]

        if group is not None:
            cmd_parts.append(group)

        cmd_parts.append(command.name)

        args = [f"<{a.name}>" for a in command.arguments]
        if args:
            cmd_parts.append(" ".join(args))

        opts = []
        for o in command.options:
            if o.short:
                opts.append(f"[-{o.short}|--{o.name}]")
            else:
                opts.append(f"[--{o.name}]")

        if opts:
            cmd_parts.append(" ".join(opts))

        with open(page_file, "w") as fp:
            doc = Document(command.name)

            if command.description:
                doc.add(Paragraph(command.description))

            doc.add(Heading("Usage", level=1))
            doc.add(Command(cmd_parts))

            if args:
                # arguments table
                doc.add(Heading("Arguments", level=1))
                header = ["Argument", "Type", "Description", "Example"]
                doc.add(
                    Table(header=header, rows=args_rows(command.arguments), bold=True)
                )

            if opts:
                # options table
                doc.add(Heading("Options", level=1))
                header = ["Option", "Type", "Description", "Default", "Example"]
                doc.add(
                    Table(header=header, rows=opts_rows(command.options), bold=True)
                )

            doc.write(fp)

    def _write_enums_page(self):
        page_file = os.path.join(self.reference_pages_dir, f"enums.md")

        with open(page_file, "w") as fp:
            doc = Document("Enums")
            doc.add(Paragraph("Enumerations used by the project."))

            for e in self.app.schemas.enums:
                name = re.sub("[^A-Za-z]", "", e.name.title())
                doc.add(Heading(name=name, level=1))

                if e.description:
                    doc.add(Paragraph(e.description))

                header = ["Key", "Value"]
                rows = [[sandwich(k, "`"), v] for k, v in e.items.items()]
                doc.add(Table(header=header, rows=rows, bold=True))

            doc.write(fp)
