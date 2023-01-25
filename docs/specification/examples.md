# Examples

Here you can find a few examples for the YAML specification for command line applications.

## Brandon

The first one is the specification for Brandon itself, also available in the main repo.

```yaml
name: Brandon
version: 0.0.1
description: An utility to create command line applications from their YAML specifications.
tags: ['cli', 'stub', 'docs']
authors:
- name: Weslley Morellato Bueno
  email: morellato.weslley@gmail.com
  url: https://github.com/wmorellato
license: MIT License
url: https://github.com/wmorellato/brandon
languages: ['python']
schemas:
  enums:
    languages:
      description: Supported languages to create application stubs.
      items:
        python: python
        bash: bash
        java: java
    python-arg-libs:
      description: Supported Python libraries for parsing command line arguments.
      items:
        click: click
cli:
  generate:
    description: Generation of different parts of the project.
    arguments:
      filename:
        description: The path to the CLI Specification file describing the application.
        type: string
    commands:
      project:
        description: Generate the project structure and the command line interface from the CLI specification file pointed by FILENAME.
        options:
          overwrite:
            description: If there is a project folder in the path pointed by `output-path` option, overwrites its contents.
            short: f
            type: flag
          language:
            description: Overwrite the default output language, which is defined from the first language provided in the `languages` key.
            short: l
            type: string
            example: java
          output-path:
            description: Set the output path for the project folder.
            type: string
            short: o
            default: Current directory
      docs:
        description: Generate the project documentation using MkDocs from the CLI specification file pointed by FILENAME.
        options:
          output-path:
            description: Set the output path for the documentation.
            type: string
            short: o
            default: Current directory
      summary:
        description: Generate a summary of the command line interface, to be used somewhere else, from the CLI specification file pointed by FILENAME.
  version:
    description: Show the version and exit.
```