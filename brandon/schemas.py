from enum import Enum


class Languages(Enum):
    """Supported languages to create application stubs."""

    PYTHON = "python"
    PYTHON_SCRIPT = "python-single"

    @classmethod
    def is_supported(cls, value):
        return value in [i.value for i in cls]


class PythonArgLibs(Enum):
    """Supported Python libraries for parsing command line arguments."""

    CLICK = "click"
