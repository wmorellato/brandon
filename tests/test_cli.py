import os
import yaml

import pytest
from click.testing import CliRunner

from brandon.cli.generate import project, docs


@pytest.fixture
def project_spec():
    return {
        "name": "Sample",
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
        "cli": {
            "test": {"description": "Test command."},
        },
    }


def test_generate_project(tmp_path, project_spec):
    yml_spec = os.path.join(tmp_path, "project.yml")
    with open(yml_spec, "w") as fp:
        yaml.dump(project_spec, fp)

    runner = CliRunner()
    result = runner.invoke(project, [str(yml_spec), "--output-path", tmp_path])

    print(result.output)
    assert result.exit_code == 0
    assert (
        result.output
        == f"Project folder for `{project_spec['name']}` created successfully in `{tmp_path}`\n"
    )


def test_generate_docs(tmp_path, project_spec):
    yml_spec = os.path.join(tmp_path, "project.yml")
    with open(yml_spec, "w") as fp:
        yaml.dump(project_spec, fp)

    runner = CliRunner()
    result = runner.invoke(docs, [str(yml_spec), "--output-path", tmp_path])

    assert result.exit_code == 0
    assert (
        result.output
        == f"Documentation folder for `{project_spec['name']}` created successfully in `{tmp_path}`\n"
    )
    assert os.path.exists(os.path.join(tmp_path, "sample-docs", "mkdocs.yml"))


def test_malformed_yaml(tmp_path):
    yml_spec = os.path.join(tmp_path, "project.yml")
    with open(yml_spec, "w") as fp:
        fp.write("foo")

    runner = CliRunner()
    result = runner.invoke(project, [str(yml_spec), "--output-path", tmp_path])

    assert result.exit_code == 1
