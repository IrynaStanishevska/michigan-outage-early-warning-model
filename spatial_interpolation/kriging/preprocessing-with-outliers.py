import pandas as pd

def detect_outliers(df, param_name, lower_q=0.10, upper_q=0.90):
    """
    return two dataframes:
    df_clean without outliers,
    df_outliers only outliers.
    """
    lower = df[param_name].quantile(lower_q)
    upper = df[param_name].quantile(upper_q)
    mask  = (df[param_name] < lower) | (df[param_name] > upper)
    return df[~mask].copy(), df[mask].copy()
