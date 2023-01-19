# Specification - 0.1.0

Specification to describe a machine-readeable structure of a command line application. The CLI application description can be passed to Brandon to create a stub command line application in different languages and also automatically build documentation.

> **Note**  
> Required fields are marked with **\***

## Application Object

This is the root object of the specification and provides general information about the application.

| **Field**      | **Type**                                 | **Description**                                            |
|----------------|------------------------------------------|------------------------------------------------------------|
| `name`*        | string                                   | The application name. Spaces are allowed.                  |
| `version`*     | string                                   | The application version, following any standards you want. |
| `description`* | string                                   | A short description of the application.                    |
| `tags`         | array\[string\]                          | A list of tags related to the application.                 |
| `authors`*     | array\[[Author Object](#author-object)\] | A list of contributing authors to the application.         |
| `license`      | string                                   | The name of the license used by the application.           |
| `url`          | string                                   | The URL of the application source code.                    |
| `languages`    | array\[string\]                          | A list of programming languages used in the application.   |
| `schemas`      | [Schema Object](#schema-object)          | Schema definitions used by the application.                |
| `cli`*         | CLI Object                               | The command line interface.                                |

### Example

```yaml
name: My Application
version: 0.0.1
description: A sample description.
tags: ['tag1', 'tag2']
authors:
- name: Jane Doe
  email: janedoe@mail.com
  url: https://github.com/janedoe
license: MIT License
url: https://github.com/foo/bar
languages: ['python', 'shell']
schemas:
    ...
cli:
    ...
```

## Author Object

This object is a simple description of the parties involved in the project.

| Pattern | Type   | Description                                         |
|---------|--------|-----------------------------------------------------|
| `name`* | string | The person's name or full name.                     |
| `email` | string | The person's email address.                         |
| `url`   | string | A personal or professional URL owned by the person. |

## Schema Object

Define application schemas that are visible to the user. For now it doesn't support custom schemas, only enumerations and in the near future global parameters to be referenced by commands.

| Field   | Type                        | Description                                                   |
|---------|-----------------------------|---------------------------------------------------------------|
| `enums` | [Enum Object](#enum-object) | Enumerations used by the application and exposed to the user. |

## Enum Object

You can use enumerations to limit a given argument or option to a set of choices or to simply describe internal logic of the application.

| Pattern   | Type                                  | Description                  |
|-----------|---------------------------------------|------------------------------|
| `{name}`* | [Enum Item Object](#enum-item-object) | The name of the enumeration. |

## Enum Item Object

| Field         | Type                                  | Description                              |
|---------------|---------------------------------------|------------------------------------------|
| `description` | string                                | A short description for this enumeration |
| `items`       | [Key Value Object](#key-value-object) | The enumeration key. It MUST be unique.  |

## Key Value Object

| Pattern    | Type                              | Description                              |
|------------|-----------------------------------|------------------------------------------|
| `{key}`*   | string                            | The enumeration key. It MUST be unique.  |
| `{value}`* | [Data Type Enum](#data-type-enum) | The value for they key.                  |

### Example

The example below defines two enumerations, the first for document formats supported by the application and the second for a list of supported encodings.

#### Definition

```yaml
schemas:
    enumerations:
        formats:
            description: Supported formats to export text.
            items:
                pdf: pdf
                word: docx
                markdown: md
                html: html
        encodings:
            description: Supported encodings for reading data.
            items:
                ascii: 0
                utf-8: 1
                utf-16: 2
```

## CLI Object

This object contains mappings between command/group names and their definitions.

| Pattern   | Type                                                                                   | Description                                                                                                                                                       |
|-----------|----------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `{name}`* | [Command Item Object](#command-item-object) \| [Group Item Object](#group-item-object) | The command to a single or group of operations in the application. This name SHOULD be lowercase and SHOULD contain only alpha characters, underscores or dashes. |
| `enums`   | [Enum Object](#enum-object)                                                            | Enumerations used in the application to be used as a fixed set of choices for certain commands.                                                                   |

### Example

The example below defines a group of commands named `services` and the generic `help` command.

#### Definition

```yaml
...
cli:
    services:
        ...
    help:
        ...
```

#### Usage

`$ my-application services <operation>`  
`$ my-application help`  

## Group Item Object

An object that describes a group of related commands. Note that it is not allowed to nest groups of commands.

| Field         | Type                                  | Description                                                         |
|---------------|---------------------------------------|---------------------------------------------------------------------|
| `description` | string                                | A short description to be applied to all commands under this group. |
| `arguments`   | [Parameter Object](#parameter-object) | The arguments common to all commands under this group               |
| `options`     | [Parameter Object](#parameter-object) | The options common to all commands under this group.                |
| `commands`*   | [Command Object](#command-object)     | Mapping of command names and their definitions.                     |

### Example

Using the same example as above, the snippet below defines a group of commands named `get`, which could be used to get different types of objects managed by the application.

#### Definition

```yaml
...
cli:
    services:
        description: Perform operations on services managed by the application.
        commands:
            start:
                ...
            stop:
                ...

```

#### Usage

`$ my-application services start`  
`$ my-application services stop`  

## Command Object

| Pattern   | Type                                        | Description                                                                                                              |
|-----------|---------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| `{name}`* | [Command Item Object](#command-item-object) | The name of an operation. This name SHOULD be lowercase and SHOULD contain only alpha characters, underscores or dashes. |

## Command Item Object

This object defines a command that maps to a single operation in the application. The command MAY have positional arguments and options to alter its behavior.

| Field         | Type                                  | Description                                                                |
|---------------|---------------------------------------|----------------------------------------------------------------------------|
| `description` | string                                | A short description for this specific operation.                           |
| `notes`       | string                                | Additional notes for this command. Mainly to be used in the documentation. |
| `arguments`   | [Parameter Object](#parameter-object) | The positional arguments used by this command.                             |
| `options`     | [Parameter Object](#parameter-object) | The options used by this command.                                          |

### Example

The example below defines the `start` command under the `services` group.

#### Definition

```yaml
...
cli:
    services:
        description: Perform operations on services managed by the application.
        commands:
            start:
                description: Start one or more named services in the application.
                arguments:
                    ...
                options:
                    ...

```

#### Usage

`$ my-application services start`

## Parameter Object

| Pattern   | Type                                                                   | Description                                                                                                               |
|-----------|------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| `{name}`* | [Argument Object](#argument-object) \| [Option Object](#option-object) | The name of the parameter. This name SHOULD be lowercase and SHOULD contain only alpha characters, underscores or dashes. |

## Argument Item Object

Used to define a *positional* parameter for the given operation. Arguments MUST have types, as most CLI libraries check types when parsing the command line. It's also useful to provide an example and a description. These parameters are *required* by default.

The name of the argument will be used as the name of the variable that will hold the value after parsing. (Isso vale pra bibliotecas de outras linguagens?)

| Field         | Type                    | Description                                               |
|---------------|-------------------------|-----------------------------------------------------------|
| `description` | string                  | A short description for this argument.                    |
| `type`*       | [Type Enum](#type-enum) | The type of this argument. Check the list of types below. |
| `example`     | string                  | An example value for this argument.                       |

### Example

Taking `systemctl` `restart` command as an example, we'll define the `unit` argument, which is the name of the unit to be restarted.

#### Definition

```yaml
...
cli:
    restart:
        description: Start or restart one or more units.
        arguments:
            unit:
                description: The name of the unit to be restarted.
                type: string
                example: NetworkManager
```

#### Usage

`# systemctl restart NetworkManager.service`

## Option Object

Used to the define an option to be passed to the command to alter the command's default behavior.

As it is with [arguments](#argument-object), options also MUST define a type. Some options' default values may be easily guessed (e.g. `--show-wide` implies that the default value is `false`), but it's recommended to set the default value for options nonetheless.

Options may also provide a short name (e.g. `-a` for `--all` in `ls`), but this is not required.

| Field         | Type                    | Description                                                 |
|---------------|-------------------------|-------------------------------------------------------------|
| `description` | string                  | A short description for this option.                        |
| `short`       | string                  | The short name of this option. *Don't* prepend dashes here. |
| `type`*       | [Type Enum](#type-enum) | The type of this option. Check the list of types below.     |
| `default`     | [type]                  | The default value for this option.                          |
| `example`     | string                  | An example value for this option.                           |

### Example

Using the same example of the `systemctl` application, we can define the `--host` option, which makes `systemctl` to operate on a remote host.

#### Definition

```yaml
...
cli:
    restart:
        description: Start or restart one or more units.
        arguments:
            ...
        options:
            host:
                description: Operate on remote host.
                short: H
                type: string
                example: john@remote.host
```

#### Usage

`# systemctl --host root@10.0.2.15 restart NetworkManager.service`

## Type Enum

List of types supported in arguments and options.

| Type   |
|--------|
| int    |
| float  |
| string |
| bool   |
| flag   |


## Data Type Enum

| Type   |
|--------|
| int    |
| float  |
| string |
