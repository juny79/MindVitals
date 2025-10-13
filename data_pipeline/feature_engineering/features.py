import pandas as pd

def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "hrv_rmssd" in df and "hr" in df:
        df["ans_balance"] = (df["hrv_rmssd"].fillna(0) * 0.2) - (df["hr"].fillna(0) * 0.1)
    return df
