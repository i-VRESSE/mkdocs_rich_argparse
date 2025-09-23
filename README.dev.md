# `mkdocs_rich_argparse` developer documentation

If you're looking for user documentation, go [here](README.md).

## Development install

```shell
# Create a virtual environment, e.g. with
python -m venv env

# activate virtual environment
source env/bin/activate

# make sure to have a recent version of pip and setuptools
python -m pip install --upgrade pip setuptools

# (from the project root directory)
# install mkdocs_rich_argparse as an editable package
python -m pip install --no-cache-dir --editable .
# install development dependencies
python -m pip install --no-cache-dir --editable .[dev]
# install documentation dependencies only
python -m pip install --no-cache-dir --editable .[docs]
```

Afterwards check that the install directory is present in the `PATH` environment variable.

## Running the tests

In an activated virtual environment with the development tools installed:

```shell
pytest -v
```

### Test coverage

In addition to just running the tests to see if they pass, they can be used for coverage statistics, i.e. to determine how much of the package's code is actually executed during tests.
In an activated virtual environment with the development tools installed, inside the package directory, run:

```shell
coverage run
```

This runs tests and stores the result in a `.coverage` file.
To see the results on the command line, run

```shell
coverage report
```

`coverage` can also generate output in HTML and other formats; see `coverage help` for more information.## Running linters locally

For linting and sorting imports we will use [ruff](https://docs.astral.sh/ruff/). Running the linters requires [uv](https://docs.astral.sh/uv) installed.

```shell
# linter
uvx ruff check .

# linter with automatic fixing
uvx ruff check . --fix
```

### (3/3) GitHub

Don't forget to also make a [release on GitHub](https://github.com/i-VRESSE/mkdocs_rich_argparse/releases/new).