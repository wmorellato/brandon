import os
import yaml
import pytest

from brandon.spec import Parser


@pytest.fixture
def sample_module():
    return '''import click
from foo import bar


@my_dec
@click.command()
@click.option("-o", "--opt", type=str, default=os.getcwd())
def my_function(opt):
    """My test function"""


if __name__ == "__main__":
    my_function()

'''


@pytest.fixture
def project_spec():
    return {
        "name": "Sample App",
        "license": "MIT License",
        "tags": [
            "foo",
        ],
        "url": "https://github.com/foo/bar",
        "description": "Sample desc",
        "languages": ["python"],
        "version": "1.0.0",
        "authors": [
            {
                "name": "Author",
                "email": "author@foo.bar",
                "url": "https://foo.bar/author",
            }
        ],
        "schemas": {
            "enums": {
                "enum1": {"description": "Some enum", "items": {"key1": "value1"}}
            }
        },
        "cli": {
            "group1": {
                "description": "Test group",
                "arguments": {
                    "arg1": {"description": "Global argument", "type": "string"}
                },
                "commands": {
                    "comm1": {
                        "description": "Test command 1",
                        "arguments": {
                            "arg2": {"description": "Local argument", "type": "int"}
                        },
                    },
                    "comm3": {
                        "description": "Test command 2",
                    },
                },
            },
            "comm2": {
                "description": "Test command 2",
                "options": {"opt1": {"description": "Option 1", "type": "flag"}},
            },
        },
    }


@pytest.fixture
def app(tmp_path, project_spec):
    yml_spec = os.path.join(tmp_path, "project.yml")
    with open(yml_spec, "w") as fp:
        yaml.dump(project_spec, fp)

    return Parser(yml_spec).app
