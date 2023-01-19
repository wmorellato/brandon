import pytest
from io import StringIO

from brandon.md_utils import (
    Document,
    Heading,
    Paragraph,
    Table,
    UnorderedList,
    Link,
    Command,
)


example_doc = """# Title

## Heading 1

Paragraph 1

Paragraph 2

### Heading 2

Paragraph 3

## Heading 3

Paragraph 4

"""

example_table = """| *Col1* | *Col2* | *Col3* |
|---|---|---|
| 0 | 0 | 0 |
| 1 | 1 | 1 |
| 2 | 2 | 2 |

"""

example_list = """- 0
- 1
- 2

"""


def test_structure():
    doc = Document(title="Title")
    doc.add(Heading(name="Heading 1", level=1))
    doc.add(Paragraph(text="Paragraph 1"))
    doc.add(Paragraph(text="Paragraph 2"))
    doc.add(Heading(name="Heading 2", level=2))
    doc.add(Paragraph(text="Paragraph 3"))
    doc.add(Heading(name="Heading 3", level=1))
    doc.add(Paragraph(text="Paragraph 4"))

    buffer = StringIO()
    doc.write(stream=buffer)
    buffer.seek(0)
    assert buffer.read() == example_doc


def test_table():
    def mock_gen():
        for i in range(0, 3):
            yield [i, i, i]

    header = ["Col1", "Col2", "Col3"]
    table = Table(header=header, rows=mock_gen(), bold=True)
    assert table.render() == example_table

    table = Table(header=header, rows=[[0, 0, 0], [1, 1, 1], [2, 2, 2]], bold=True)
    assert table.render() == example_table

    header = ["Col1", "Col2", "Col3", "Col4"]
    table = Table(header=header, rows=mock_gen())
    with pytest.raises(Exception):
        table.render()


def test_simple_list():
    def mock_gen():
        for i in range(0, 3):
            yield i

    ulist = UnorderedList(items=mock_gen())
    assert ulist.render() == example_list


def test_link():
    link = Link(text="Foo", url="bar")
    assert link.render() == "[Foo](bar)"


def test_command():
    command = Command(args=["ls", "-a", "/tmp"])
    assert command.render() == "`$ ls -a /tmp`\n\n"

    command = Command(args=["ls", "-a", "/tmp"], root=True)
    assert command.render() == "`# ls -a /tmp`\n\n"
