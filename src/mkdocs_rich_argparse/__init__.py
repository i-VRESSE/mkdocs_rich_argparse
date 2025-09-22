"""Documentation about mkdocs_rich_argparse."""

import argparse
import importlib
import io
from collections.abc import Callable
from textwrap import dedent
import mkdocs.config.base
import mkdocs.config.config_options
import mkdocs.plugins
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.structure.files import File
from mkdocs.structure.files import Files
from rich.console import Console
from rich.text import Text
from rich_argparse import ArgumentDefaultsRichHelpFormatter

__version__ = "0.1.0"

logger = mkdocs.plugins.get_plugin_logger(__name__)


def _capture_help(parser: argparse.ArgumentParser) -> str:
    """Capture the help text of an argparse parser as HTML."""
    # Based on https://github.com/hamdanal/rich-argparse/blob/e28584ac56ddd46f4079d037c27f24f0ec4eccb4/rich_argparse/_argparse.py#L545
    # but with export instead of save

    # Overwrite default colors as on mkdocs black text is not visible in dark mode
    ArgumentDefaultsRichHelpFormatter.styles["argparse.help"] = "green"
    ArgumentDefaultsRichHelpFormatter.styles["argparse.text"] = "green"

    text = Text.from_ansi(parser.format_help())
    console = Console(file=io.StringIO(), record=True)
    console.print(text, crop=False)
    code_format = dedent("""\
        <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
        <code style="font-family:inherit">
        {code}
        </code>
        </pre>
    """)
    return console.export_html(code_format=code_format, inline_styles=True)


# TODO allow to configure heading
def _argparser_to_markdown(parser: argparse.ArgumentParser, heading: str = "CLI Reference") -> str:
    prog = parser.prog

    main_help = _capture_help(parser)

    lines = [
        f"# {heading}",
        f"Documentation for the `{prog}` script.",
        "```console",
        f"{prog} --help",
        "```",
        main_help,
    ]

    subparsers_actions = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)]
    current_subparsers_action = subparsers_actions[0]

    for sub_cmd_name, sub_cmd_parser in current_subparsers_action.choices.items():
        sub_cmd_help_text = _capture_help(sub_cmd_parser)

        lines.extend(
            [
                f"## {sub_cmd_name}",
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
                        f"## {sub_cmd_name} {sub_sub_cmd_name}",
                        "```console",
                        f"{prog} {sub_cmd_name} {sub_sub_cmd_name} --help",
                        "```",
                        sub_sub_cmd_help_text,
                    ]
                )

    return "\n".join(lines)


class MkDocRichArgparseError(PluginError):
    """Base exception for mkdocs_rich_argparse."""


def _load_parser(module: str, attribute: str) -> argparse.ArgumentParser:
    """Load and return the argparse parser located at '<module>:<attribute>'."""
    factory = _load_obj(module, attribute)

    if not callable(factory):
        msg = f"{attribute!r} must be a callable that returns an 'argparse.ArgumentParser' object"
        raise MkDocRichArgparseError(msg)

    parser = factory()

    if not isinstance(parser, argparse.ArgumentParser):
        msg = f"{attribute!r} must be a 'argparse.ArgumentParser' object, got {type(parser)}"
        raise MkDocRichArgparseError(msg)

    return parser


def _load_obj(module: str, attribute: str) -> Callable:
    try:
        mod = importlib.import_module(module)
    except SystemExit:
        msg = "the module appeared to call sys.exit()"
        raise MkDocRichArgparseError(msg) from None

    try:
        return getattr(mod, attribute)
    except AttributeError as exc:
        msg = f"Module {module!r} has no attribute {attribute!r}"
        raise MkDocRichArgparseError(msg) from exc


class RichArgparsePluginConfig(mkdocs.config.base.Config):
    """Configuration for the RichArgparsePlugin."""

    module = mkdocs.config.config_options.Type(str)
    factory = mkdocs.config.config_options.Type(str)


class RichArgparsePlugin(mkdocs.plugins.BasePlugin[RichArgparsePluginConfig]):
    """MkDocs plugin to generate documentation for a rich argparse parser."""

    def on_files(self, files: Files, config: MkDocsConfig) -> Files:
        """Add a generated cli.md file to the documentation."""
        logger.info("Generating CLI documentation...")
        parser = _load_parser(self.config.module, self.config.factory)
        docs_content = _argparser_to_markdown(parser)
        # TODO instead of adding file replace cli.md with generated content
        # like https://github.com/mkdocs/mkdocs-click/blob/master/mkdocs_click/_extension.py
        cli_md_file = File.generated(
            config=config,
            # TODO make cli.md path configurable
            src_uri="cli.md",
            content=docs_content,
        )
        files.append(cli_md_file)
        return files
