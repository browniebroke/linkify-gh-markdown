from pathlib import Path
from typing import Annotated

import typer

from .main import linkify

app = typer.Typer()


@app.command()
def main(
    input_path: str,
    heading_level: Annotated[
        int | None,
        typer.Option(
            "--heading-level",
            help="Set the top heading level in the output (1-6).",
            min=1,
            max=6,
        ),
    ] = None,
) -> None:
    """Add the arguments and print the result."""
    content = Path(input_path).read_text()
    print(linkify(content, heading_level=heading_level))
