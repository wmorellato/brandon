# Docs Builder

Documentation is created and built using [MkDocs](https://www.mkdocs.org/), with [Material](https://squidfunk.github.io/mkdocs-material/) as the default theme.

There's a lot of customization that can be done to the site, including changing colors, fonts, icons and add custom JS/CSS code. I recommend checking both resources above so you can customize the website according to your needs.

## Documentation Structure

The documentation has the following structure. The `docs` directory contain the Markdown files for the actual pages. Groups have their own folders inside, and inside them, each command has a separate Markdown file.

The `mkdocs.yml` file is required by MkDocs to build the website. You can edit this file to customize it.

```
{app}-docs
├── docs
│   ├── index.md
│   └── reference
│       ├── enums.md
│       └── {group}
│           └── {command}.md
└── mkdocs.yml
```