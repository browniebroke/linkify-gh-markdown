from pathlib import Path

import typer
from rich import print

from .main import linkify

app = typer.Typer()


@app.command()
def main(input_path: str) -> None:
    """Add the arguments and print the result."""
    content = Path(input_path).read_text()
    print(linkify(content))
