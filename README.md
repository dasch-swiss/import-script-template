# Template repo for import scripts

## Quick Start

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
source .venv/bin/activate
pre-commit install
```


## Run the scripts

```bash
python -m src.main
```


## Run the type checkers, linters, and tests

Check your type hints:

```bash
mypy .
```

Auto-format your code:

```bash
ruff format .
```

Check if there are linting erros:

```bash
ruff check .
```

Run the unit tests and e2e tests:

```bash
pytest
```


## Troubleshooting

If something doesn't work, check the following:

- Run `pwd` to check if you are at the root of the repository.
  If you're in a subfolder, your terminal commands might fail.
- Activate the virtual environment with `source .venv/bin/activate` 
- Reinstall the virtual environment with `rm -rf .venv; uv sync; source .venv/bin/activate`