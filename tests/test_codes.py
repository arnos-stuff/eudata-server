import json
import pandas as pd
from functools import reduce

from eudata_server.backend.sdmx.base import dfquery
from eudata_server.tools.paths import (
    static_dir, templates_dir, css_dir,
    js_dir, sass_dir, data_dir
)

# get metadata
units_path = data_dir / "units.json"
catscheme_path = data_dir / "toc-cat-schemes.json"
categories = json.load(open(catscheme_path,"r"))
catnames = reduce(                                                                                                                                                                                                                                                                                                                                                 
    lambda acc, new: acc + [new] if new not in acc else acc,
    [c["category_scheme_name"] for c in categories],
    []
    )
dfu = pd.read_json(units_path, orient="records")


dataflow_id = "tec00016"
df = dfquery(dataflow_id)
columns = df.columns.tolist()
textCode = df["unit"].unique()[0]
textUnit = dfu.loc[dfu["code"].str.lower() == textCode.lower(), "description"].values[0]

if "TIME_PERIOD" in columns:
    dftp = df.loc[df["OBS_VALUE"].isna(), ["TIME_PERIOD", "OBS_VALUE"]].groupby("TIME_PERIOD").count()
    if not len(dftp):
        result = df["TIME_PERIOD"].max()
    else:
        print(dftp)
# print(textUnit)
# print(textCode)
print(dftp)