# project

Generate the project structure and the command line interface from the CLI specification file pointed by FILENAME.

## Usage

`$ brandon generate project <filename> [-f|--overwrite] [-l|--language] [-o|--output-path]`

## Arguments

| *Argument* | *Type* | *Description* | *Example* |
|---|---|---|---|
| `filename` | string | The path to the CLI Specification file describing the application. |  |

## Options

| *Option* | *Type* | *Description* | *Default* | *Example* |
|---|---|---|---|---|
| `overwrite` | flag | If there is a project folder in the path pointed by `output-path` option, overwrites its contents. |  |  |
| `language` | string | Overwrite the default output language, which is defined from the first language provided in the `languages` key. |  | java |
| `output-path` | string | Set the output path for the project folder. | Current directory |  |

