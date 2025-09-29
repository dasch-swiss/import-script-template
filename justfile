# List all recipies
default:
    @just --list

type-check:
    mypy .
    
format:
    ruff format .

lint:
    ruff check .
