## Mkdocs rich argparse

[![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/i-VRESSE/mkdocs_rich_argparse)
[![github license badge](https://img.shields.io/github/license/i-VRESSE/mkdocs_rich_argparse)](https://github.com/i-VRESSE/mkdocs_rich_argparse)
[![RSD](https://img.shields.io/badge/rsd-mkdocs_rich_argparse-00a3e3.svg)](https://research-software-directory.org/software/mkdocs-rich-argparse)
[![workflow pypi badge](https://img.shields.io/pypi/v/mkdocs_rich_argparse.svg?colorB=blue)](https://pypi.org/project/mkdocs-rich-argparse)
[![fair-software badge](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu)
[![CI](https://github.com/i-VRESSE/mkdocs_rich_argparse/actions/workflows/build.yml/badge.svg)](https://github.com/i-VRESSE/mkdocs_rich_argparse/actions/workflows/build.yml)

An MkDocs plugin to generate documentation for a [rich argparse parser](https://pypi.org/project/rich-argparse/).
It renders commands, sub commands and sub-sub commands which can have rich help messages.

## Installation

```bash
pip install mkdocs-rich-argparse
```

## Usage

**TL;DR:** Set `package` to your installed CLI package's project name and add
`cli.md` to your navigation.

1. Define your commands in your package's `pyproject.toml` using `[project.scripts]`:

   ```toml
   [project]
   name = "my-package"

   [project.scripts]
   myprogram = "my_package.cli:main"
   mysecondprogram = "my_package.cli:download"
   ```

2. Ensure your CLI package is installed alongside the plugin so its script
   metadata is available.

3. In `mkdocs.yml`, set `package` to the `[project].name` value from your
   `pyproject.toml` and add the generated page to your navigation:

   ```yaml
   plugins:
       - mkdocs-rich-argparse:
           package: my-package

   nav:
       - CLI Reference: cli.md
   ```

Parsers are captured at `parse_args()` or `parse_known_args()`. Code before
parsing still executes during the documentation build.

See the [example/](example/) directory for a minimal example and a custom styled example.

[![Screenshot of example](https://github.com/i-VRESSE/mkdocs_rich_argparse/raw/main/example/screenshot.png)](https://github.com/i-VRESSE/mkdocs_rich_argparse/raw/main/example/screenshot.png)

## Configuration

`package` is required. All other plugin settings are optional and belong under
`mkdocs-rich-argparse` in `mkdocs.yml`:

| Setting | Default | Description |
| --- | --- | --- |
| `src_uri` | `cli.md` | Generated page path relative to the docs directory. Update `nav` to match. |
| `heading` | `CLI Reference` | Top-level heading of the generated page. |
| `order` | `[]` | Script names to document first, in the specified order. |
| `styles` | See below | Rich styles for the generated help text. |

For example, customize the page path and heading and put your main script first:

```yaml
plugins:
  - mkdocs-rich-argparse:
      package: my-package
      src_uri: reference/commands.md
      heading: Commands
      order:
        - myprogram

nav:
  - Commands: reference/commands.md
```

Scripts listed in `order` appear first, in the specified order.
All remaining scripts are sorted alphabetically.
Unknown or duplicate script names cause a build error.
If no `order` is specified, all scripts are sorted alphabetically.

### Styles

The `styles` mapping accepts Rich style strings for `args`, `groups`, `help`,
`metavar`, `syntax`, `text`, and `default`. The plugin sets `help` and `text` to
`green` by default so they remain visible in dark mode. Other values keep the
current `RichHelpFormatter` styles unless overridden.

```yaml
plugins:
  - mkdocs-rich-argparse:
      package: my-package
      styles:
        args: bright_red
        groups: bright_green
        metavar: bright_magenta
        syntax: dark_orange
        help: bright_cyan
        text: bright_yellow
        default: bright_black
```

## Colors in Continuous Integration

To preserve Rich colors in CI, set these
[environment variables](https://rich.readthedocs.io/en/stable/console.html#environment-variables)
(GitHub Actions example):

```yaml
env:
    TTY_COMPATIBLE: '1'
    TTY_INTERACTIVE: '0'
```

## Contributing

If you want to contribute to the development of mkdocs_rich_argparse,
have a look at the [contribution guidelines](CONTRIBUTING.md).
