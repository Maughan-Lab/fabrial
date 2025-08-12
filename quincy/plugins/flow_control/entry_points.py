from pathlib import Path


def get_item_directories() -> list[Path]:
    """Get the item initialization directories."""
    return [Path(__file__).parent.joinpath("item_initialization")]
