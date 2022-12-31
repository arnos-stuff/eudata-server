import pandas as pd
import numpy as np

df = pd.DataFrame({
    'TIME_PERIOD': [
        2022,
        2022,
        2022,
        2012,
        2021,
        2021,
        2021,
        2021,
        2009,
        2009,
        2009,
        2009,
        2009,
        2009,
    ],
    'OBS_VALUE': [
        np.nan,
        np.nan,
        2022,
        3.2,
        33.2,
        21.2,
        np.nan,
        1.2,
        2.2,
        200,
        209,
        1.09,
        1.09,
        2.09,
    ]
})

dftp = df[df["OBS_VALUE"].isna()].value_counts("TIME_PERIOD").reset_index()

dftp_recent = dftp[dftp["TIME_PERIOD"] > 2015]

if len(dftp_recent):
    result = dftp_recent["TIME_PERIOD"].min()
else:
    result = df["TIME_PERIOD"].max()