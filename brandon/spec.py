import re
import yaml
import logging
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Types(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    FLAG = "flag"


@dataclass
class Argument:
    name: str
    type: Types
    description: str = field(default=None)
    example: str = field(default=None)


@dataclass
class Option:
    name: str
    type: Types
    description: str = field(default=None)
    short: str = field(default=None)
    default: str = field(default=None)
    example: str = field(default=None)


@dataclass
class Group:
    name: str
    description: str
    commands: list


@dataclass
class Command:
    name: str
    description: str
    arguments: list
    options: list


@dataclass
class CLI:
    commands: list
    groups: list


@dataclass
class Author:
    name: str
    email: str
    url: str


@dataclass
class EnumObject:
    name: str
    description: str
    items: dict


@dataclass
class Schemas:
    enums: list[EnumObject] = field(default_factory=list)


@dataclass
class Application:
    name: str
    version: str
    description: str
    cli: CLI
    exec: str
    schemas: Schemas
    tags: list = field(default_factory=list)
    authors: list = field(default_factory=list)
    license: str = field(default=None)
    url: str = field(default=None)
    languages: list = field(default=None)


class Parser:
    """Parser for applications defined using the YAML
    specification.
    """

    REQUIRED_APP = ["name", "description", "version"]

    def __init__(self, filename):
        with open(filename) as fp:
            self.data = yaml.safe_load(fp)

        self._parse_app()

    def _normalize_name(self, name: str, dash_map="_") -> str:
        return re.sub("[^A-Za-z0-9_-]", "", name).lower().replace("-", dash_map)

    def _parse_app(self):
        for field in self.REQUIRED_APP:
            if field not in self.data:
                raise Exception(
                    "Field `%s` is required for `Application` object" % field
                )

        authors = self._parse_authors()
        schemas = self._parse_schemas()
        cli = self._parse_cli()

        self.app = Application(
            name=self.data["name"],
            exec=self._normalize_name(self.data["name"]),
            version=self.data["version"],
            description=self.data["description"],
            tags=self.data.get("tags", None),
            authors=authors,
            license=self.data.get("license", None),
            url=self.data.get("url", None),
            languages=self.data.get("languages", None),
            schemas=schemas,
            cli=cli,
        )

    def _parse_authors(self):
        authors = []

        for ao in self.data["authors"]:
            if type(ao) != dict or "name" not in ao:
                raise Exception("Author must be defined using the `Author` object")

            name = ao["name"]
            email = ao.get("email", None)
            url = ao.get("url", None)
            authors.append(Author(name=name, email=email, url=url))

        return authors

    def _parse_schemas(self):
        enums = []

        if "schemas" not in self.data:
            return Schemas()

        for name, object in self.data["schemas"]["enums"].items():
            enums.append(self._parse_enum(name, object))

        return Schemas(enums=enums)

    def _parse_enum(self, enum_name, object):
        description = object.get("description", None)

        logger.debug("Found enum `%s`", enum_name)

        if "items" not in object:
            raise Exception("You must declare the `items` field, even if it's empty")

        return EnumObject(
            name=enum_name, description=description, items=object["items"]
        )

    def _parse_cli(self):
        groups = []
        commands = []

        for name, object in self.data["cli"].items():
            if "commands" in object:
                groups.append(self._parse_group(name, object))
            else:
                commands.append(self._parse_command(name, object))

        return CLI(commands=commands, groups=groups)

    def _parse_group(self, group_name, object):
        group_name = self._normalize_name(group_name)
        description = object.get("description", None)
        commands = []

        logger.debug("Found group `%s`", group_name)

        for name, command in object["commands"].items():
            comm = self._parse_command(name, command)

            if "arguments" in object:
                for name, arg in object["arguments"].items():
                    comm.arguments.append(self._parse_argument(name, arg))

            if "options" in object:
                for name, opt in object["options"].items():
                    comm.options.append(self._parse_option(name, opt))

            commands.append(comm)

        return Group(name=group_name, description=description, commands=commands)

    def _parse_command(self, cmd_name, object):
        cmd_name = self._normalize_name(cmd_name)
        description = object.get("description", None)
        arguments = []
        options = []

        logger.debug("Found command `%s`", cmd_name)

        if "arguments" in object:
            for name, arg in object["arguments"].items():
                arguments.append(self._parse_argument(name, arg))

        if "options" in object:
            for name, arg in object["options"].items():
                options.append(self._parse_option(name, arg))

        return Command(
            name=cmd_name, description=description, arguments=arguments, options=options
        )

    def _parse_argument(self, arg_name, object):
        arg_name = self._normalize_name(arg_name)

        if "type" not in object:
            raise Exception("Missing type for `%s` argument" % arg_name)

        logger.debug("Found argument `%s`", arg_name)

        type = Types(object["type"])
        description = object.get("description", None)
        example = object.get("example", None)

        return Argument(
            name=arg_name, type=type, description=description, example=example
        )

    def _parse_option(self, opt_name, object):
        opt_name = self._normalize_name(opt_name)

        if "type" not in object:
            raise Exception("Missing type for `%s` option" % opt_name)

        logger.debug("Found option `%s`", opt_name)

        type = Types(object["type"])
        description = object.get("description", None)
        short = object.get("short", None)
        default = object.get("default", None)
        example = object.get("example", None)

        return Option(
            name=opt_name,
            type=type,
            description=description,
            short=short,
            default=default,
            example=example,
        )
