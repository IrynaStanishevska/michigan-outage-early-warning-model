import pandas as pd
import geopandas as gpd
from preprocessing import detect_outliers
from kriging import kriging_one_year, spatial_joint_with_outliers

PARAM_NAME = 'dwpf'          # parameter name
MAXLAG     = 250_000

if __name__ == "__main__":
    # read files
    df_2021_raw = pd.read_csv("data/2021_raw.csv",  parse_dates=['valid'])
    df_2022_raw = pd.read_csv("data/2022_raw.csv",  parse_dates=['valid'])
    df_grid     = pd.read_csv("data/gis_prepared.csv")

    # outliers
    df_2021_prep, df_2021_out = detect_outliers(df_2021_raw, PARAM_NAME)
    df_2022_prep, df_2022_out = detect_outliers(df_2022_raw, PARAM_NAME)

    # kriging 2021
    df_krig_2021 = kriging_one_year(df_2021_prep, df_grid, PARAM_NAME, MAXLAG)
    df_final_2021 = spatial_joint_with_outliers(
        df_krig_2021, df_2021_out, PARAM_NAME
    )
    df_final_2021.to_csv(f"{PARAM_NAME}_krig_2021.csv", index=False)
    print("Saved", f"{PARAM_NAME}_krig_2021.csv")

    # kriging 2022
    df_krig_2022 = kriging_one_year(df_2022_prep, df_grid, PARAM_NAME, MAXLAG)
    df_final_2022 = spatial_joint_with_outliers(
        df_krig_2022, df_2022_out, PARAM_NAME
    )
    df_final_2022.to_csv(f"{PARAM_NAME}_krig_2022.csv", index=False)
    print("Saved", f"{PARAM_NAME}_krig_2022.csv")
