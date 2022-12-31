import rich
import json
import requests
import pandas as pd

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
    df = query(
        dataflow_id=dataflow_id,
        fmt='SDMX-CSV',
        lang='en',
        )
    df = df.drop(columns=["DATAFLOW", "LAST UPDATE"])
    return df