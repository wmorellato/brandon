from brandon.builders.summary import Builder


summary_sample = """Sample App - Sample desc

Usage:
    sampleapp [command]

Commands:
    sampleapp group1 comm1|comm3     Test group
    sampleapp comm2                  Test command 2

Authors:
    Author <author@foo.bar>"""


def test_summary_creation(app):
    assert Builder(app=app).build() == summary_sample
