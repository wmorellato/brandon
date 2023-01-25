from abc import ABC
from dataclasses import dataclass, field
import typing
from io import IOBase


class TextElement(ABC):
    def render(self):
        raise NotImplementedError()

    def __str__(self):
        return self.render()


@dataclass
class Paragraph(TextElement):
    text: str

    def render(self):
        return f"{self.text}\n\n"


@dataclass
class Heading(TextElement):
    """Level 1 corresponds to a double heading mark (##)
    in the document as a single one (#) is reserved for
    the title.
    """

    name: str
    level: int

    def render(self):
        return f"{'#'*(self.level+1)} {self.name}\n\n"


@dataclass
class Table(TextElement):
    """Represents a table in the document,

    The `bold` parameter determines if the header should be
    in bold or not.

    It's advised to pass rows as a generator, rather than the
    entire set of rows.
    """

    header: list
    rows: typing.Iterable[typing.Collection]
    bold: bool = field(default=True)

    def render(self):
        ncol = len(self.header)
        lines = []
        bread = " *" if self.bold else " "

        fmt_header = [sandwich(h, bread) for h in self.header]
        lines.append(lasagna(fmt_header, "|"))
        lines.append(lasagna(["---"] * ncol, "|"))

        for r in self.rows:
            if len(r) != ncol:
                raise Exception("Row %s has wrong size (should be %s)" % (r, ncol))

            fmt_row = [sandwich(i, " ") for i in r]
            lines.append(lasagna(fmt_row, "|"))

        return "\n".join(lines) + "\n" * 2


@dataclass
class UnorderedList(TextElement):
    items: list

    def render(self):
        lines = []
        for i in self.items:
            lines.append(f"- {i}")

        return "\n".join(lines) + "\n" * 2


@dataclass
class Link(TextElement):
    text: str
    url: str

    def render(self):
        return f"[{self.text}]({self.url})"


@dataclass
class Command(TextElement):
    args: list
    root: bool = field(default=False)

    def render(self):
        marker = "$" if not self.root else "#"
        return f"`{marker} {' '.join(self.args)}`\n\n"


class Document:
    def __init__(self, title: str) -> None:
        self._elements = []
        self._elements.append(Heading(name=title, level=0))

    def add(self, element: TextElement):
        if not isinstance(element, TextElement):
            raise Exception("Not a valid object")

        self._elements.append(element)

    def write(self, stream: IOBase):
        if not isinstance(stream, IOBase) or not stream.writable():
            raise Exception("Stream not writable")

        for l in self._elements:
            stream.write(l.render())


def sandwich(filling: str, bread: str, mirror=True):
    a = bread
    b = bread[::-1] if mirror else bread
    return f"{a}{filling}{b}"


def lasagna(filling: list, noodle: str):
    inner = noodle.join(filling)
    return f"{noodle}{inner}{noodle}"
