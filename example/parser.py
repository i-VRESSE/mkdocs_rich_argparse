import argparse
from rich_argparse import RichHelpFormatter


def sample_parser() -> argparse.ArgumentParser:
    """Create a sample argparse parser with subcommands."""
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
    remove_parser.add_argument("name", help="Name of the remote to remove. Some `syntax` here.", metavar="REMOTE_NAME")
    return parser


def main() -> None:
    """Run the example console script."""
    sample_parser().parse_args()


def download() -> None:
    """Parse arguments for a curl-inspired console script."""
    parser = argparse.ArgumentParser(
        prog="mysecondprogram",
        description="Transfer data from a URL.",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument("url", help="URL to transfer")
    parser.add_argument("-o", "--output", metavar="FILE", help="Write output to a file instead of stdout")
    parser.parse_args()
