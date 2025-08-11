from os import PathLike
from pathlib import Path

from quincy.utility import descriptions
from quincy.utility.descriptions import DescriptionInfo, Substitutions

FILES_DIRECTORY = Path(__file__).parent.joinpath("files")


def compare_lines(actual_text: str, expected_file: PathLike[str] | str):
    """
    Compare the lines of **actual_text** against the lines contained in **expected_file**. This
    makes it easier to see where the text doesn't match up.
    """
    with open(expected_file, "r") as f:
        expected_text = f.read()
    for actual_line, expected_line in zip(actual_text.splitlines(), expected_text.splitlines()):
        assert actual_line == expected_line


def test_no_description_info():
    """Tests `descriptions.make_descriptions()` with a `None` argument."""
    # if no `DescriptionInfo` is provided there should be a default description
    assert descriptions.make_description(None) == "No description provided."


def test_everything():
    """Tests `descriptions.make_descriptions()` with substitutions in all files."""
    everything_directory = FILES_DIRECTORY.joinpath("everything")
    text = descriptions.make_description(
        DescriptionInfo(
            everything_directory,
            "everything",
            Substitutions(
                {"SUBSTITUTION": "overview substitution text"},
                {"PARAMETER3": "Parameter3Substitution"},
                {"SUBSTITUTION": "visuals substitution text"},
                {"FILE3": "file3substitution.txt"},
            ),
        )
    )
    compare_lines(text, everything_directory.joinpath("correct.md"))


def test_substitution_errors():
    """Tests `descriptions.make_descriptions()` with missing substitutions."""
    substitution_errors_directory = FILES_DIRECTORY.joinpath("substitution_errors")
    # the data directory name doesn't matter here
    # we provide no substitutions when there are substitutions in the files, which should yield the
    # error text
    text = descriptions.make_description(DescriptionInfo(substitution_errors_directory, ""))
    compare_lines(text, substitution_errors_directory.joinpath("correct.md"))


def test_toml_errors():
    """Tests `descriptions.make_descriptions()` with TOML errors."""
    toml_errors_directory = FILES_DIRECTORY.joinpath("toml_errors")
    # the data directory name doesn't matter here
    text = descriptions.make_description(DescriptionInfo(toml_errors_directory, ""))
    compare_lines(text, toml_errors_directory.joinpath("correct.md"))


def test_missing_files():
    """Tests `descriptions.make_descriptions()` with missing description files."""
    missing_files_directory = FILES_DIRECTORY.joinpath("missing_files")
    # the data directory name doesn't matter here
    text = descriptions.make_description(DescriptionInfo(missing_files_directory, ""))
    compare_lines(text, missing_files_directory.joinpath("correct.md"))
