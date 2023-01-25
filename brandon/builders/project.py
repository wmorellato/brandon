import os

from brandon.builders.languages import *
from brandon.schemas import Languages


BUILDER_MAP = {
    Languages.PYTHON: PythonBuilder,
    Languages.PYTHON_SCRIPT: PythonScriptBuilder,
}


class Project:
    def __init__(self, app, language, output_path, overwrite=False) -> None:
        self.app = app
        self.language = language
        self.output_path = output_path
        self.overwrite = overwrite
        self.builder = None

        if language in BUILDER_MAP:
            self.builder = BUILDER_MAP[language](app=app, output_path=output_path)

    def create(self):
        if self.builder is None:
            raise Exception(f"Unsupported language `{self.language}`")

        if os.path.exists(self.builder.project_root) and not self.overwrite:
            print(self.builder.project_root)
            raise Exception(
                "Output folder already exists. Either use the flag `--overwrite` to overwrite the contents of this directory or change the app version in your `cli.yml`."
            )

        self.builder.build()
