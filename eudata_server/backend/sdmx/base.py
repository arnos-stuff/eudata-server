import rich
import json
import requests
import numpy as np
import pandas as pd

from functools import reduce
from typing import Union, List, Dict, Any, Optional

formats = [
    "SDMX-CSV",
    "JSON",
    "TSV",
]

def query(
    dataflow_id: str,
    fmt: Optional[str] = "JSON",
    lang: Optional[str] = "en",
    ):
    if fmt not in formats:
        raise ValueError(f"Format must be one of {formats}")

    base_url = "https://ec.europa.eu/eurostat/api/dissemination"
    data_url = f"{base_url}/sdmx/2.1/data/{dataflow_id}?format={fmt}&lang={lang}"
    response = requests.get(data_url)

    lang_error = f"ERR_LANGUAGE: Language {lang.upper()} is not supported for {dataflow_id.upper()}"
    if lang_error in response.text:
        raise ValueError(lang_error + f" in format {fmt}")

    if fmt == "JSON":
        return response.json()
    elif fmt == "TSV":
        return response.text
    elif fmt == "SDMX-CSV":
        lines = response.text.split("\r\n")
        columns = lines[0].split(",")
        records = []
        for line in lines[1:]:
            record = {}
            for colname, value in zip(columns, line.split(",")):
                record[colname] = value
            records.append(record)
        df = pd.DataFrame.from_records(records)
        return df
    else:
        return response

def head(
    dataflow_id: str,
    n: Optional[int] = 10,
    fmt: Optional[str] = "JSON",
    lang: Optional[str] = "en",
    ):
    if fmt not in formats:
        raise ValueError(f"Format must be one of {formats}")

    base_url = "https://ec.europa.eu/eurostat/api/dissemination"
    head_data_url = f"{base_url}/sdmx/2.1/data/{dataflow_id}?format={fmt}&lang={lang}&firstNObservations={n}"
    response = requests.get(head_data_url)

    lang_error = f"ERR_LANGUAGE: Language {lang.upper()} is not supported for {dataflow_id.upper()}"
    if lang_error in response.text:
        raise ValueError(lang_error + f" in format {fmt}")

    if fmt == "JSON":
        return response.json()
    elif fmt == "TSV":
        return response.text
    elif fmt == "SDMX-CSV":
        lines = response.text.split("\r\n")
        columns = lines[0].split(",")
        records = []
        for line in lines[1:]:
            record = {}
            for colname, value in zip(columns, line.split(",")):
                record[colname] = value
            records.append(record)
        df = pd.DataFrame.from_records(records)
        return df
    else:
        return response


def dfquery(
    dataflow_id: str,
    ):
    """Query a dataflow and return a dataframe.

    Args:
        dataflow_id (str): The dataflow id.
    
    Returns:
        pd.DataFrame: The dataframe.
    """
    df = query(
        dataflow_id=dataflow_id,
        fmt='SDMX-CSV',
        lang='en',
        )
    df = df.drop(columns=["DATAFLOW", "LAST UPDATE"])
    return df


def get_time_period(df: pd.DataFrame, threshold: int = 2015) -> int:
    """Get the most recent time period in a dataframe, or None if no time period is found.
    
    When several time periods are found, the most recent one is returned.
    When the value column is empty for a certain amount of rows, this routine
    returns the most recent time period which has the least amount of empty values.
    
    Args:
        df (pd.DataFrame): The dataframe to query.
        threshold (int, optional): The threshold for the most recent time period. Defaults to 2015.
        
    Returns:
        int: The most recent time period."""

    if "TIME_PERIOD" not in df.columns:
        return None

    df.columns = df.columns.str.upper()
        
    dftp = df[(df["OBS_VALUE"].isna()) | (df["OBS_VALUE"] == '')].value_counts("TIME_PERIOD").reset_index()

    dftp_recent = dftp[dftp["TIME_PERIOD"].apply(quarters_to_float) > threshold]

    if len(dftp_recent):
        result = dftp_recent["TIME_PERIOD"].apply(quarters_to_float).min()
    else:
        result = df["TIME_PERIOD"].apply(quarters_to_float).max()
    return int(result)

def get_text_unit(df: pd.DataFrame, df_units: pd.DataFrame) -> str:
    df.columns = df.columns.str.upper()
    columns = df.columns.tolist()
    text_code = df["UNIT"].unique()[0]
    text_unit = df_units.loc[
        df_units["code"].str.lower() == text_code.lower(),
        "description"].values[0]
    return text_unit


def agg(sequence: Any, method: str = "median") -> Any:
    """Aggregate a sequence of values.
    
    Args:
        sequence (Any): The sequence to aggregate.
        method (str, optional): The method to use for aggregation. Defaults to "first".
        
    Returns:
        Any: The aggregated value.
    """
    if not len(sequence):
        return 0

    if method == "first":
        return sequence[0]
    elif method == "last":
        return sequence[-1]
    elif method == "mean":
        return np.mean(sequence)
    elif method == "sum":
        return np.sum(sequence)
    elif method == "min":
        return np.min(sequence)
    elif method == "max":
        return np.max(sequence)
    elif method == "median":
        return np.median(sequence)
    else:
        raise ValueError(f"Method {method} not supported")

def guess_nuts_lvl(df: pd.DataFrame) -> int:
    """Guess the NUTS level of a eurostat dataset.
    
    A national code is `BE` or `CZ`. That means two letters.
    A regional code is `BE2` or `CZ1` or `CZZ`. That means 3 characters.
    And it goes on like that.
    We'll guess the NUTS level by counting the number of characters in the GEO column minus 2.
    """
    ignore = ["EU27_2020", "EU28", "EA19"]
    df.columns = df.columns.str.upper()
    nuts_lvl = df[df.GEO.notna()].GEO.apply(
        lambda code: len(code) - 2 if code not in ignore else 0
    ).max()
    return nuts_lvl

def quarters_to_float(quarter: str) -> float:
    """Convert a quarter to a float.

    A quarter is a string like `2010-Q1`.

    Q1 will be converted to 0.25, Q2 to 0.5, Q3 to 0.75 and Q4 to 1.0.
    
    Args:
        quarter (str): The quarter to convert.
        
    Returns:
        float: The float.
    """
    if isinstance(quarter, (int, float)):
        return float(quarter)
    elif "-Q" not in quarter:
        return float(quarter)
    else:
        year, quarter = quarter.split("-Q")
        return float(year) + float(quarter) / 4.0

def setup_chrmap(df: pd.DataFrame, agg_method: str = 'median') -> Dict[str, str]:
    """Setup a character map for a dataframe.
    
    Args:
        df (pd.DataFrame): The dataframe to setup the character map for.
        
    Returns:
        Dict[str, str]: The character map.
    """
    df.columns = df.columns.str.upper()
    time_period = get_time_period(df)
    dftp = df[
        (df["TIME_PERIOD"].apply(quarters_to_float) == time_period) &
        (df["OBS_VALUE"].notna()) &
        (df["OBS_VALUE"] != '')
        ]
    dfgu = dftp.groupby(["GEO", "UNIT"]).agg({"OBS_VALUE": agg_method}).reset_index()
    dfgu = dfgu.dropna()
    
    units = dftp["UNIT"].unique()

    data = {}
    for unit in units:
        data[unit] = dfgu[dfgu["UNIT"] == unit].set_index("GEO").to_dict()["OBS_VALUE"]

    num_units = len(units)

    if num_units > 2:
        raise ValueError("More than 2 units found")
    else:
        maptype = "ch" if num_units == 1 else "chbi"
    
    if "GEO" in df.columns:
        geos = df["GEO"].unique()
    else:
        raise ValueError("No geo column found")

    result = {
        "maptype": maptype,
        "time_period": time_period,
        "units": units.tolist(),
        "num_units": num_units,
        "geos": geos.tolist(),
        "data": data,
        "time_period": int(time_period) if time_period else None,
        "columns": df.columns.tolist(),
        "nuts_lvl": guess_nuts_lvl(df),
    }
    return result