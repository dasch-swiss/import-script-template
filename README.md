# Template repo for import scripts

## Quick Start

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
source .venv/bin/activate
pre-commit install
brew install just
echo XMLLIB_WARNINGS_CSV_SAVEPATH="xmllib_warnings.csv" >> .env
```


## Run the scripts

```bash
python -m src.main
```


## Run the type checkers, linters, and tests

Check your type hints:

```bash
just type-check
```

Auto-format your code:

```bash
just format
```

Check if there are linting errors:

```bash
just lint
```

Run the tests:

```bash
pytest
```


## Troubleshooting

If something doesn't work, check the following:

- Run `pwd` to check if you are at the root of the repository.
  If you're in a subfolder, your terminal commands might fail.
- Activate the virtual environment with `source .venv/bin/activate`
- Reinstall the virtual environment with `rm -rf .venv; uv sync; source .venv/bin/activate`
