import os

from brandon.builders.languages.python import Builder, Module, Decorator


def test_module(tmp_path, sample_module):
    mod = Module(name="module", path=tmp_path, imports=["click", "foo.bar"])
    dec_noparams = Decorator(name="my_dec", no_params=True)
    dec_comm = Decorator(name="click.command")
    dec_opt = Decorator(
        name="click.option",
        args=['"-o"', '"--opt"'],
        kwargs={"type": "str", "default": "os.getcwd()"},
    )
    mod.add_function(
        name="my_function",
        params=["opt"],
        decorators=[dec_noparams, dec_comm, dec_opt],
        comment="My test function",
    )
    mod.add_main(function_name="my_function")
    mod.write()

    mod = Module(name="__init__", path=tmp_path)
    mod.write()

    with open(os.path.join(tmp_path, "module.py")) as fp:
        content = fp.read()
        assert content == sample_module

    assert os.path.exists(os.path.join(tmp_path, "__init__.py"))


def test_project_structure(tmp_path, app):
    Builder(app=app, output_path=tmp_path).build()
    proj_folder = os.path.join(tmp_path, f"{app.exec}-{app.version}")
    source_folder = os.path.join(proj_folder, app.exec)
    tests_folder = os.path.join(proj_folder, "tests")

    assert os.path.exists(tests_folder)

    assert os.path.exists(os.path.join(source_folder, "cli", "__init__.py"))
    for g in app.cli.groups:
        assert os.path.exists(os.path.join(source_folder, "cli", f"{g.name}.py"))

    assert os.path.exists(os.path.join(source_folder, "__init__.py"))
    assert os.path.exists(os.path.join(source_folder, "main.py"))


def test_support_files(tmp_path, app):
    Builder(app=app, output_path=tmp_path).build()
    proj_folder = os.path.join(tmp_path, f"{app.exec}-{app.version}")

    assert os.path.exists(os.path.join(proj_folder, "README.md"))
    assert os.path.exists(os.path.join(proj_folder, "pyproject.toml"))
    # assert os.path.exists(os.path.join(proj_folder, "cli.yml"))
