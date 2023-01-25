import os
import yaml

from brandon.builders.docs import Builder


def test_config_file(tmp_path, app):
    Builder(app=app, output_path=tmp_path).build()
    config_file = os.path.join(tmp_path, f"{app.exec}-docs", "mkdocs.yml")

    with open(config_file) as fp:
        config = yaml.full_load(fp)

    assert config["site_name"] == app.name
    assert config["theme"]["name"] == "material"
    assert config["repo_url"] == app.url
    assert config["nav"] == [
        {"Home": "index.md"},
        {
            "Reference": [
                {
                    "Commands": [
                        {
                            "group1": [
                                {"comm1": "reference/group1/comm1.md"},
                                {"comm3": "reference/group1/comm3.md"},
                            ]
                        },
                        {"comm2": "reference/comm2.md"},
                    ]
                },
                {"Schemas": [{"Enums": "reference/enums.md"}]},
            ]
        },
    ]


def test_page_creation(tmp_path, app):
    Builder(app=app, output_path=tmp_path).build()
    pages_dir = os.path.join(tmp_path, f"{app.exec}-docs", "docs")
    ref_pages_dir = os.path.join(pages_dir, "reference")

    with open(os.path.join(pages_dir, "index.md")) as fp:
        content = fp.read()
        assert content.startswith(f"# {app.name}")

    with open(os.path.join(ref_pages_dir, "group1", "comm1.md")) as fp:
        content = fp.read()
        assert content.startswith(f"# comm1")

    with open(os.path.join(ref_pages_dir, "comm2.md")) as fp:
        content = fp.read()
        assert content.startswith(f"# comm2")

    with open(os.path.join(ref_pages_dir, "enums.md")) as fp:
        content = fp.read()
        assert content.startswith(f"# Enums")
