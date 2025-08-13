from os import PathLike
from pathlib import Path

from quincy.utility.descriptions import FilesDescription, Substitutions, TextDescription

FILES_DIRECTORY = Path(__file__).parent.joinpath("files")


# helper
def compare_lines(actual_text: str, expected_text: str):
    """
    Compare the lines of **actual_text** against the lines of **expected_text**. This
    makes it easier to see where the text doesn't match up.
    """
    for actual_line, expected_line in zip(actual_text.splitlines(), expected_text.splitlines()):
        assert actual_line == expected_line


# helper
def compare_lines_from_file(actual_text: str, expected_file: PathLike[str] | str):
    """Call `compare_lines()` with **actual_text** and the contents of **expected_file**."""
    with open(expected_file, "r") as f:
        expected_text = f.read()
    compare_lines(actual_text, expected_text)


# --------------------------------------------------------------------------------------------------
# tests for `FilesDescription` class
def test_everything():
    """Tests `descriptions.make_descriptions()` with substitutions in all files."""
    everything_directory = FILES_DIRECTORY.joinpath("everything")
    text = FilesDescription(
        everything_directory,
        "everything",
        Substitutions(
            {"SUBSTITUTION": "overview substitution text"},
            {"PARAMETER3": "Parameter3Substitution"},
            {"SUBSTITUTION": "visuals substitution text"},
            {"FILE3": "file3substitution.txt"},
        ),
    ).render()
    compare_lines_from_file(text, everything_directory.joinpath("correct.md"))


def test_substitution_errors():
    """Tests `descriptions.make_descriptions()` with missing substitutions."""
    substitution_errors_directory = FILES_DIRECTORY.joinpath("substitution_errors")
    # the data directory name doesn't matter here
    # we provide no substitutions when there are substitutions in the files, which should yield the
    # error text
    text = FilesDescription(substitution_errors_directory, "").render()
    compare_lines_from_file(text, substitution_errors_directory.joinpath("correct.md"))


def test_toml_errors():
    """Tests `descriptions.make_descriptions()` with TOML errors."""
    toml_errors_directory = FILES_DIRECTORY.joinpath("toml_errors")
    # the data directory name doesn't matter here
    text = FilesDescription(toml_errors_directory, "").render()
    compare_lines_from_file(text, toml_errors_directory.joinpath("correct.md"))


def test_missing_files():
    """Tests `descriptions.make_descriptions()` with missing description files."""
    missing_files_directory = FILES_DIRECTORY.joinpath("missing_files")
    # the data directory name doesn't matter here
    text = FilesDescription(missing_files_directory, "").render()
    compare_lines_from_file(text, missing_files_directory.joinpath("correct.md"))


# --------------------------------------------------------------------------------------------------
# tests for `TextDescription` class
def test_text():
    """Tests `TextDescription.render()`."""
    description_provider = TextDescription(
        "Random Directory",
        "Overview text.",
        {"Parameter1": "Description of Parameter1.", "Parameter2": "Description of Parameter2."},
        {"file1.txt": "Description of file1.txt.", "file2.txt": "Description of file2.txt."},
        "Visuals text.",
    )
    compare_lines_from_file(
        description_provider.render(), FILES_DIRECTORY.joinpath("correct_for_text.md")
    )
