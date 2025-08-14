from typing import Any

import polars as pl


def add_to_dataframe(dataframe: pl.DataFrame, data_to_add: dict[Any, Any]) -> pl.DataFrame:
    """
    Create a DataFrame from **data_to_add** and horizontally concatenate it with **dataframe**.
    The original dataframe's data is concatenated *to the right* of the new data.
    """
    return pl.concat((pl.DataFrame(data_to_add), dataframe), how="horizontal")
