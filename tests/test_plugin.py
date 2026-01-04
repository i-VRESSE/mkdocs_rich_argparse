import argparse
from textwrap import dedent
import pytest
from rich_argparse import RichHelpFormatter
from mkdocs_rich_argparse import RichArgparseStyles
from mkdocs_rich_argparse import argparser_to_markdown


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
    monkeypatch.setenv("FORCE_COLOR", "1")

    result = argparser_to_markdown(sample_parser, heading="My Program CLI")

    assert len(result) > 3500
    assert '<span style="color: #008080; text-decoration-color: #008080">' in result


@pytest.fixture
def plain_parser():
    """Parser using default HelpFormatter (the common case)."""
    parser = argparse.ArgumentParser(prog="plainprog", description="A plain parser.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose mode")
    subparsers = parser.add_subparsers(title="commands", dest="command")
    sub = subparsers.add_parser("run", help="Run something")
    sub.add_argument("target", help="Target to run")
    return parser


def test_plain_parser_gets_colors(monkeypatch: pytest.MonkeyPatch, plain_parser: argparse.ArgumentParser):
    """Verify parsers without RichHelpFormatter still get colored output."""
    monkeypatch.setenv("FORCE_COLOR", "1")

    result = argparser_to_markdown(plain_parser)

    # Should have color spans from RichHelpFormatter
    assert '<span style="color:' in result
    # Should have the program name
    assert "plainprog" in result


def test_plain_parser_formatter_not_mutated(plain_parser: argparse.ArgumentParser):
    """Verify original formatter_class is restored after capture."""
    original_formatter = plain_parser.formatter_class

    argparser_to_markdown(plain_parser)

    assert plain_parser.formatter_class is original_formatter
    assert plain_parser.formatter_class is not RichHelpFormatter


def test_subparser_formatter_not_mutated(plain_parser: argparse.ArgumentParser):
    """Verify subparser formatter_class is also restored."""
    # Get the subparser
    subparsers_action = next(a for a in plain_parser._actions if isinstance(a, argparse._SubParsersAction))
    run_parser = subparsers_action.choices["run"]
    assert isinstance(run_parser, argparse.ArgumentParser)
    original_formatter = run_parser.formatter_class

    argparser_to_markdown(plain_parser)

    assert run_parser.formatter_class is original_formatter
    assert run_parser.formatter_class is not RichHelpFormatter


def test_prog_style_option(monkeypatch: pytest.MonkeyPatch, plain_parser: argparse.ArgumentParser):
    """Verify prog style option is applied to RichHelpFormatter."""
    monkeypatch.setenv("FORCE_COLOR", "1")

    # Configure prog style
    styles = RichArgparseStyles()
    styles.prog = "#ff0000"
    styles.apply()

    result = argparser_to_markdown(plain_parser)

    # Should have the custom prog color in the output
    assert "#ff0000" in result or "rgb(255,0,0)" in result.lower() or "color: #ff0000" in result.lower()


def test_all_style_options_recognized():
    """Verify all style options are recognized by the config."""
    styles = RichArgparseStyles()

    # All these should be valid attributes
    expected_styles = ["prog", "args", "groups", "help", "metavar", "syntax", "text", "default"]
    for style_name in expected_styles:
        assert hasattr(styles, style_name), f"Missing style option: {style_name}"
