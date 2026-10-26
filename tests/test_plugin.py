import argparse
import sys
from importlib.metadata import EntryPoint
from pathlib import Path
from textwrap import dedent
from types import ModuleType
import pytest
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import PluginCollection
from mkdocs.structure.files import Files
from rich_argparse import RichHelpFormatter
from mkdocs_rich_argparse import MkDocRichArgparseError
from mkdocs_rich_argparse import RichArgparsePlugin
from mkdocs_rich_argparse import _entry_points_to_markdown
from mkdocs_rich_argparse import _load_entry_point_parser
from mkdocs_rich_argparse import argparser_to_markdown

EXPECTED = Path(__file__).parent / "expected"


@pytest.fixture
def sample_parser():
    parser = argparse.ArgumentParser(
        prog="myprogram", description="This is my program.", formatter_class=RichHelpFormatter
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose mode")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    remote_parser = subparsers.add_parser("remote", help="Manage remote connections", formatter_class=RichHelpFormatter)
    remote_subparsers = remote_parser.add_subparsers(title="remote subcommands", dest="remote_subcommand")
    remove_parser = remote_subparsers.add_parser(
        "remove", help="Remove a remote connection", formatter_class=RichHelpFormatter
    )
    remove_parser.add_argument("name", help="Name of the remote to remove")
    return parser


def test_argparser_to_markdown_with_no_color(sample_parser: argparse.ArgumentParser):
    result = argparser_to_markdown(sample_parser, heading="My Program CLI")

    expected = dedent("""\
        # My Program CLI
        Documentation for the `myprogram` script.
        ```console
        myprogram --help
        ```
        <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
        <code style="font-family:inherit" class="nohighlight">
        Usage: myprogram [-h] [--verbose] {remote} ...

        This is my program.

        Options:
          -h, --help  show this help message and exit
          --verbose   Enable verbose mode

        Subcommands:
          {remote}
            remote    Manage remote connections

        </code>
        </pre>

        ## remote
        ```console
        myprogram remote --help
        ```
        <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
        <code style="font-family:inherit" class="nohighlight">
        Usage: myprogram remote [-h] {remove} ...

        Options:
          -h, --help  show this help message and exit

        Remote Subcommands:
          {remove}
            remove    Remove a remote connection

        </code>
        </pre>

        ## remote remove
        ```console
        myprogram remote remove --help
        ```
        <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
        <code style="font-family:inherit" class="nohighlight">
        Usage: myprogram remote remove [-h] name

        Positional Arguments:
          name        Name of the remote to remove

        Options:
          -h, --help  show this help message and exit

        </code>
        </pre>
    """)

    assert result == expected


def test_argparser_to_markdown_with_color(monkeypatch: pytest.MonkeyPatch, sample_parser: argparse.ArgumentParser):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("TERM", "xterm")
    monkeypatch.setenv("FORCE_COLOR", "1")

    result = argparser_to_markdown(sample_parser, heading="My Program CLI")

    assert result == (EXPECTED / "colored-cli.md").read_text()


@pytest.fixture
def sample_parser_without_subcommands():
    parser = argparse.ArgumentParser(
        prog="myprogram", description="This is my program.", formatter_class=RichHelpFormatter
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose mode")
    return parser


def test_argparser_to_markdown_without_subcommands(sample_parser_without_subcommands: argparse.ArgumentParser):
    result = argparser_to_markdown(sample_parser_without_subcommands, heading="My Program CLI")

    expected = dedent("""\
        # My Program CLI
        Documentation for the `myprogram` script.
        ```console
        myprogram --help
        ```
        <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
        <code style="font-family:inherit" class="nohighlight">
        Usage: myprogram [-h] [--verbose]

        This is my program.

        Options:
          -h, --help  show this help message and exit
          --verbose   Enable verbose mode

        </code>
        </pre>
    """)

    assert result == expected


@pytest.fixture
def installed_scripts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Install lightweight distribution metadata and CLI modules for discovery."""
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    metadata = tmp_path / "example_cli-1.0.dist-info"
    metadata.mkdir()
    (metadata / "METADATA").write_text("Name: example-cli\nVersion: 1.0\n")
    # Nonalphabetical metadata order must also be preserved in the generated page.
    (metadata / "entry_points.txt").write_text(
        "[console_scripts]\nexample-score = example_cli:score\nexample = example_cli:main\n"
        "[other_group]\nignored = example_cli:main\n"
    )
    (tmp_path / "example_cli.py").write_text(
        dedent("""\
        import argparse

        def make_parser():
            parser = argparse.ArgumentParser(description="Example command")
            parser.add_argument("input", help="Input file")
            commands = parser.add_subparsers()
            commands.add_parser("run", prog="example run", help="Run the command")
            return parser

        def main() -> None:
            make_parser().parse_args()
            raise RuntimeError("CLI work must not run")

        def score():
            parser = argparse.ArgumentParser(description="Score an input")
            parser.add_argument("--score", help="Score threshold")
            parser.parse_known_args()
            raise RuntimeError("CLI work must not run")
    """)
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    return tmp_path


@pytest.mark.parametrize(
    ("options", "src_uri", "heading"),
    [
        ({"package": "Example_CLI", "src_uri": "reference/commands.md"}, "reference/commands.md", "CLI Reference"),
        ({"package": "example-cli", "heading": "Example"}, "cli.md", "Example"),
    ],
)
def test_entry_points_page(installed_scripts: Path, options: dict[str, str], src_uri: str, heading: str):
    plugin = RichArgparsePlugin()
    plugin.load_config(options)
    config = MkDocsConfig()
    config.plugins = PluginCollection()
    config.plugins._current_plugin = None
    config.site_dir = str(installed_scripts / "site")
    plugin.on_config(config)
    files = plugin.on_files(Files([]), config=config)
    expected = (EXPECTED / "entry-points.md").read_text().replace("# CLI Reference\n", f"# {heading}\n", 1)
    assert [(page.src_uri, page.content_string) for page in files] == [(src_uri, expected)]


@pytest.mark.parametrize(
    ("order", "expected"),
    [
        ([], ["example-score", "example", "example-aux"]),
        (["example"], ["example", "example-score", "example-aux"]),
        (["example-aux", "example"], ["example-aux", "example", "example-score"]),
    ],
)
def test_script_order(installed_scripts: Path, order: list[str], expected: list[str]):
    metadata = installed_scripts / "example_cli-1.0.dist-info" / "entry_points.txt"
    metadata.write_text(metadata.read_text().replace("[other_group]", "example-aux = example_cli:main\n[other_group]"))
    plugin = RichArgparsePlugin()
    errors, warnings = plugin.load_config({"package": "example-cli", "order": order})
    assert not errors
    assert not warnings
    config = MkDocsConfig()
    config.plugins = PluginCollection()
    config.plugins._current_plugin = None
    config.site_dir = str(installed_scripts / "site")
    plugin.on_config(config)
    files = plugin.on_files(Files([]), config=config)
    page = next(iter(files))
    headings = [line.removeprefix("## ") for line in page.content_string.splitlines() if line.startswith("## ")]
    assert headings == expected


@pytest.mark.parametrize("order", ["example", [1]])
def test_invalid_order_config(order: object):
    plugin = RichArgparsePlugin()
    errors, _ = plugin.load_config({"package": "example-cli", "order": order})
    assert [key for key, _ in errors] == ["order"]


@pytest.mark.parametrize(
    ("order", "message"),
    [
        (["missing"], "Unknown console scripts.*missing"),
        (["example", "example"], "duplicate console script names"),
    ],
)
@pytest.mark.usefixtures("installed_scripts")
def test_invalid_script_order(order: list[str], message: str):
    with pytest.raises(MkDocRichArgparseError, match=message):
        _entry_points_to_markdown("example-cli", "CLI", order)


@pytest.mark.parametrize(
    "options",
    [
        {},
        {"module": "example_cli"},
        {"factory": "make_parser"},
    ],
)
def test_invalid_parser_source(options: dict[str, str]):
    plugin = RichArgparsePlugin()
    errors, _ = plugin.load_config(options)
    assert [key for key, _ in errors] == ["package"]


def test_empty_distribution():
    plugin = RichArgparsePlugin()
    plugin.load_config({"package": ""})
    with pytest.raises(MkDocRichArgparseError, match="non-empty installed distribution name"):
        plugin.on_config(MkDocsConfig())


def test_missing_entry_points():
    with pytest.raises(MkDocRichArgparseError, match=r"No console_scripts.*ensure it is installed"):
        _entry_points_to_markdown("nonexistent-test-distribution", "CLI")


@pytest.mark.parametrize("body", ["pass", "raise SystemExit(2)", "raise ValueError('broken')"])
def test_entry_point_failure_restores_state(monkeypatch: pytest.MonkeyPatch, body: str):
    module = ModuleType("broken_cli")

    def main() -> None:
        if body == "raise SystemExit(2)":
            raise SystemExit(2)
        if body == "raise ValueError('broken')":
            msg = "broken"
            raise ValueError(msg)

    module.main = main
    monkeypatch.setitem(sys.modules, "broken_cli", module)
    expected = (sys.argv, argparse.ArgumentParser.parse_args, argparse.ArgumentParser.parse_known_args)
    with pytest.raises(MkDocRichArgparseError, match=r"[Cc]onsole script 'broken'"):
        _load_entry_point_parser(EntryPoint(name="broken", value="broken_cli:main", group="console_scripts"))
    assert (sys.argv, argparse.ArgumentParser.parse_args, argparse.ArgumentParser.parse_known_args) == expected
