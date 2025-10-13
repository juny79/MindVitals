import pandas as pd

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # basic sanity clean
    if "hr" in df:
        df = df[(df["hr"] > 20) & (df["hr"] < 220)]
    return df
