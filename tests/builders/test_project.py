import os
import pytest

from brandon.builders.languages import PythonBuilder
from brandon.builders.project import Project
from brandon.schemas import Languages


def test_language_choice(tmp_path, app):
    project = Project(app=app, language=Languages.PYTHON, output_path=tmp_path)
    assert isinstance(project.builder, PythonBuilder)

    project = Project(app=app, language="go", output_path=tmp_path)
    assert project.builder is None

    with pytest.raises(Exception) as e:
        project.create()
    assert str(e.value) == "Unsupported language `go`"


def test_creation(tmp_path, app):
    project_dir = os.path.join(tmp_path, f"{app.exec}-{app.version}")
    os.makedirs(project_dir)

    project = Project(app=app, language=Languages.PYTHON, output_path=tmp_path)
    with pytest.raises(Exception) as e:
        project.create()
    assert (
        str(e.value)
        == "Output folder already exists. Either use the flag `--overwrite` to overwrite the contents of this directory or change the app version in your `cli.yml`."
    )

    project = Project(
        app=app, language=Languages.PYTHON, output_path=tmp_path, overwrite=True
    )
    project.create()
    assert os.path.exists(os.path.join(project_dir, "README.md"))
