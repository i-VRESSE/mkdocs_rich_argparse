import argparse
from textwrap import dedent
import pytest
from rich_argparse import RichHelpFormatter
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
