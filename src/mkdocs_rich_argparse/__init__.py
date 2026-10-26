"""Documentation about mkdocs_rich_argparse."""

import argparse
import importlib.metadata
import io
import re
import sys
from textwrap import dedent
from unittest.mock import patch
import mkdocs.config.base
import mkdocs.config.config_options
import mkdocs.plugins
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.structure.files import File
from mkdocs.structure.files import Files
from rich.console import Console
from rich.text import Text
from rich_argparse import RichHelpFormatter

__version__ = "0.2.0"

logger = mkdocs.plugins.get_plugin_logger(__name__)


def _capture_help(parser: argparse.ArgumentParser) -> str:
    """Capture the help text of an argparse parser as HTML."""
    # Based on https://github.com/hamdanal/rich-argparse/blob/e28584ac56ddd46f4079d037c27f24f0ec4eccb4/rich_argparse/_argparse.py#L545
    # but with export instead of save

    text = Text.from_ansi(parser.format_help())
    console = Console(file=io.StringIO(), record=True)
    console.print(text, crop=False)
    code_format = dedent("""\
        <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
        <code style="font-family:inherit" class="nohighlight">
        {code}
        </code>
        </pre>
    """)
    return console.export_html(code_format=code_format, inline_styles=True)


def argparser_to_markdown(
    parser: argparse.ArgumentParser, heading: str = "CLI Reference", *, heading_level: int = 1
) -> str:
    """Convert an argparse parser to markdown documentation."""
    prog = parser.prog

    main_help = _capture_help(parser)

    lines = [
        f"{'#' * heading_level} {heading}",
        f"Documentation for the `{prog}` script.",
        "```console",
        f"{prog} --help",
        "```",
        main_help,
    ]

    subparsers_actions = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)]

    # Only process subcommands if they exist
    if not subparsers_actions:
        return "\n".join(lines)

    current_subparsers_action = subparsers_actions[0]

    for sub_cmd_name, sub_cmd_parser in current_subparsers_action.choices.items():
        sub_cmd_help_text = _capture_help(sub_cmd_parser)

        lines.extend(
            [
                f"{'#' * (heading_level + 1)} {sub_cmd_name}",
                "```console",
                f"{prog} {sub_cmd_name} --help",
                "```",
                sub_cmd_help_text,
            ]
        )

        # Check for sub-sub-commands
        sub_subparsers_actions = [
            action for action in sub_cmd_parser._actions if isinstance(action, argparse._SubParsersAction)
        ]
        if sub_subparsers_actions:
            sub_current_subparsers_action = sub_subparsers_actions[0]
            for sub_sub_cmd_name, sub_sub_cmd_parser in sub_current_subparsers_action.choices.items():
                sub_sub_cmd_help_text = _capture_help(sub_sub_cmd_parser)

                lines.extend(
                    [
                        f"{'#' * (heading_level + 1)} {sub_cmd_name} {sub_sub_cmd_name}",
                        "```console",
                        f"{prog} {sub_cmd_name} {sub_sub_cmd_name} --help",
                        "```",
                        sub_sub_cmd_help_text,
                    ]
                )

    return "\n".join(lines)


class MkDocRichArgparseError(PluginError):
    """Base exception for mkdocs_rich_argparse."""


class _ParserCapturedError(BaseException):
    def __init__(self, parser: argparse.ArgumentParser):
        self.parser = parser


def _load_entry_point_parser(entry_point: importlib.metadata.EntryPoint) -> argparse.ArgumentParser:
    """Capture a console script's parser before it processes arguments."""

    def capture(parser: argparse.ArgumentParser, *_args: object, **_kwargs: object) -> None:
        raise _ParserCapturedError(parser)

    try:
        with (
            patch.object(sys, "argv", [entry_point.name, "--help"]),
            patch.object(argparse.ArgumentParser, "parse_args", capture),
            patch.object(argparse.ArgumentParser, "parse_known_args", capture),
        ):
            entry_point.load()()
    except _ParserCapturedError as captured:
        return captured.parser
    except (Exception, SystemExit) as exc:
        msg = f"Could not load argparse parser for console script {entry_point.name!r}: {exc}"
        raise MkDocRichArgparseError(msg) from exc
    msg = f"Console script {entry_point.name!r} did not parse arguments with argparse"
    raise MkDocRichArgparseError(msg)


def _entry_points_to_markdown(distribution: str, heading: str, order: list[str] | None = None) -> str:
    """Document all console scripts belonging to an installed distribution."""
    normalized_name = re.sub(r"[-_.]+", "-", distribution).lower()
    scripts = [
        entry_point
        for entry_point in importlib.metadata.entry_points(group="console_scripts")
        if entry_point.dist is not None and re.sub(r"[-_.]+", "-", entry_point.dist.name).lower() == normalized_name
    ]
    if not scripts:
        msg = f"No console_scripts entry points found for distribution {distribution!r}; ensure it is installed"
        raise MkDocRichArgparseError(msg)
    if order:
        names = {entry_point.name for entry_point in scripts}
        unknown = [name for name in order if name not in names]
        if unknown:
            msg = f"Unknown console scripts in order for distribution {distribution!r}: {', '.join(unknown)}"
            raise MkDocRichArgparseError(msg)
        if len(order) != len(set(order)):
            msg = "order must not contain duplicate console script names"
            raise MkDocRichArgparseError(msg)
        positions = {name: index for index, name in enumerate(order)}
        scripts.sort(key=lambda entry_point: positions.get(entry_point.name, len(order)))
    sections = [f"# {heading}"]
    for entry_point in scripts:
        parser = _load_entry_point_parser(entry_point)
        sections.append(argparser_to_markdown(parser, heading=entry_point.name, heading_level=2))
    return "\n\n".join(sections)


class RichArgparseStyles(mkdocs.config.base.Config):
    """Configuration for styles applied to the generated documentation."""

    args = mkdocs.config.config_options.Optional(mkdocs.config.config_options.Type(str))
    groups = mkdocs.config.config_options.Optional(mkdocs.config.config_options.Type(str))
    # Overwrite default colors as on mkdocs black text is not visible in dark mode
    help = mkdocs.config.config_options.Type(str, default="green")
    metavar = mkdocs.config.config_options.Optional(mkdocs.config.config_options.Type(str))
    syntax = mkdocs.config.config_options.Optional(mkdocs.config.config_options.Type(str))
    text = mkdocs.config.config_options.Type(str, default="green")
    default = mkdocs.config.config_options.Optional(mkdocs.config.config_options.Type(str))

    def apply(self) -> None:
        """Apply the configured styles to RichHelpFormatter."""
        for key, value in self.items():
            if value is not None:
                RichHelpFormatter.styles[f"argparse.{key}"] = value


class RichArgparsePluginConfig(mkdocs.config.base.Config):
    """Configuration for the RichArgparsePlugin."""

    package = mkdocs.config.config_options.Type(str)
    src_uri = mkdocs.config.config_options.Type(str, default="cli.md")
    heading = mkdocs.config.config_options.Type(str, default="CLI Reference")
    order = mkdocs.config.config_options.ListOfItems(mkdocs.config.config_options.Type(str), default=[])
    styles = mkdocs.config.config_options.SubConfig(RichArgparseStyles)


class RichArgparsePlugin(mkdocs.plugins.BasePlugin[RichArgparsePluginConfig]):
    """MkDocs plugin to generate documentation for a rich argparse parser."""

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Validate the selected parser source."""
        if not self.config.package:
            msg = "package must be a non-empty installed distribution name"
            raise MkDocRichArgparseError(msg)
        return config

    def on_files(self, files: Files, /, *, config: MkDocsConfig) -> Files:
        """Add a generated cli.md file to the documentation."""
        logger.info("Generating CLI documentation...")
        self.config.styles.apply()
        docs_content = _entry_points_to_markdown(self.config.package, self.config.heading, self.config.order)
        cli_md_file = File.generated(
            config=config,
            src_uri=self.config.src_uri,
            content=docs_content,
        )
        files.append(cli_md_file)
        return files
