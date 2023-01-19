import os
import yaml
import pytest

from brandon.spec import Parser, Types


def test_app_parser(tmp_path, project_spec):
    yml_spec = os.path.join(tmp_path, "project.yml")
    with open(yml_spec, "w") as fp:
        yaml.dump(project_spec, fp)

    app = Parser(yml_spec).app
    assert app.exec == "sampleapp"
    assert app.name == project_spec["name"]
    assert app.license == project_spec["license"]
    assert app.tags == project_spec["tags"]
    assert app.url == project_spec["url"]
    assert app.description == project_spec["description"]
    assert app.version == project_spec["version"]
    assert app.authors[0].name == project_spec["authors"][0]["name"]


def test_missing_field(tmp_path, project_spec):
    yml_spec = os.path.join(tmp_path, "project.yml")
    del project_spec["description"]

    with open(yml_spec, "w") as fp:
        yaml.dump(project_spec, fp)

    with pytest.raises(Exception):
        Parser(yml_spec).app


def test_command_parser(tmp_path, project_spec):
    yml_spec = os.path.join(tmp_path, "project.yml")
    with open(yml_spec, "w") as fp:
        yaml.dump(project_spec, fp)

    cli = Parser(yml_spec).app.cli
    assert len(cli.commands) == 1
    assert len(cli.groups) == 1
    assert cli.commands[0].name == "comm2"
    assert cli.commands[0].description == "Test command 2"
    assert cli.commands[0].options[0].type == Types.FLAG

    assert cli.groups[0].name == "group1"
    assert cli.groups[0].commands[0].name == "comm1"
    assert cli.groups[0].commands[0].description == "Test command 1"
    assert cli.groups[0].commands[0].arguments[1].name == "arg1"
    assert cli.groups[0].commands[0].arguments[1].type == Types.STRING
    assert cli.groups[0].commands[0].arguments[1].description == "Global argument"
    assert cli.groups[0].commands[0].arguments[0].name == "arg2"
    assert cli.groups[0].commands[0].arguments[0].type == Types.INT
    assert cli.groups[0].commands[0].arguments[0].description == "Local argument"


def test_name_normalization(tmp_path, project_spec):
    yml_spec = os.path.join(tmp_path, "project.yml")
    project_spec["cli"]["grOup~"] = project_spec["cli"]["group1"]
    del project_spec["cli"]["group1"]

    project_spec["cli"]["Get-cOmm!"] = project_spec["cli"]["comm2"]
    del project_spec["cli"]["comm2"]

    with open(yml_spec, "w") as fp:
        yaml.dump(project_spec, fp)

    cli = Parser(yml_spec).app.cli
    assert cli.groups[0].name == "group"
    assert cli.commands[0].name == "get_comm"


def test_enums(tmp_path, project_spec):
    yml_spec = os.path.join(tmp_path, "project.yml")
    with open(yml_spec, "w") as fp:
        yaml.dump(project_spec, fp)

    app = Parser(yml_spec).app

    enum1 = app.schemas.enums[0]
    assert enum1.name == "enum1"
    assert len(enum1.items) == 1
    assert enum1.items["key1"] == "value1"
