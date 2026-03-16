from typer.testing import CliRunner

from linkify_gh_markdown.cli import app
from linkify_gh_markdown.main import linkify

runner = CliRunner()


def test_help():
    """The help message includes the CLI name."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Add the arguments and print the result" in result.stdout


def test_cli_output_matches_linkify(tmp_path):
    input_text = "Thanks @user-a in https://github.com/org/repo/pull/1\n"
    input_file = tmp_path / "input.md"
    input_file.write_text(input_text)

    expected = linkify(input_text)
    result = runner.invoke(app, [str(input_file)])

    assert result.exit_code == 0
    assert result.output.strip() == expected.strip()
