## Badges

(Customize these badges with your own links, and check https://shields.io/ or https://badgen.net/ to see which other badges are available.)

| fair-software.eu recommendations | |
| :-- | :--  |
| (1/5) code repository              | [![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/i-VRESSE/mkdocs_rich_argparse) |
| (2/5) license                      | [![github license badge](https://img.shields.io/github/license/i-VRESSE/mkdocs_rich_argparse)](https://github.com/i-VRESSE/mkdocs_rich_argparse) |
| (3/5) community registry           | [![RSD](https://img.shields.io/badge/rsd-mkdocs_rich_argparse-00a3e3.svg)](https://www.research-software.nl/software/mkdocs_rich_argparse) [![workflow pypi badge](https://img.shields.io/pypi/v/mkdocs_rich_argparse.svg?colorB=blue)](https://pypi.python.org/project/mkdocs_rich_argparse/) |
| (4/5) citation                     | |
| (5/5) checklist                    | [![workflow cii badge](https://bestpractices.coreinfrastructure.org/projects/<replace-with-created-project-identifier>/badge)](https://bestpractices.coreinfrastructure.org/projects/<replace-with-created-project-identifier>) |
| howfairis                          | [![fair-software badge](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu) |
| **Other best practices**           | &nbsp; |
| **GitHub Actions**                 | &nbsp; |
| Build                              | [![build](https://github.com/i-VRESSE/mkdocs_rich_argparse/actions/workflows/build.yml/badge.svg)](https://github.com/i-VRESSE/mkdocs_rich_argparse/actions/workflows/build.yml) |
| Citation data consistency          | [![cffconvert](https://github.com/i-VRESSE/mkdocs_rich_argparse/actions/workflows/cffconvert.yml/badge.svg)](https://github.com/i-VRESSE/mkdocs_rich_argparse/actions/workflows/cffconvert.yml) |## How to use mkdocs_rich_argparse

An MkDocs plugin to generate documentation for a rich argparse parser.
It renders commands, sub commands and sub-sub commands which can have rich help messages.

## Installation

Install from Pypi:

```bash
pip install mkdocs_rich_argparse
```

## Usage

In your `mkdocs.yml` configuration file, add the plugin and configure it with the module and command to document:

```yaml
plugins:
    - mkdocs_rich_argparse:
        module: my_module
        factory: my_factory_function

nav:
   - CLI Reference: cli.md
```

Where `my_module` is the Python module containing your argparse parser factory function, and `my_factory_function` is the specific function that returns an argparse parser object. It should be callable without arguments.

When serving or building your MkDocs site, the plugin will generate a `cli.md` file containing the documentation for the specified argparse parser.

## Contributing

If you want to contribute to the development of mkdocs_rich_argparse,
have a look at the [contribution guidelines](CONTRIBUTING.md).
