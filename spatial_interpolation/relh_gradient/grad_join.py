import geopandas as gpd
import pandas as pd

def attach_gradient_to_centroids(
    df_grad: pd.DataFrame,
    df_centroids: pd.DataFrame,
    crs: str = "EPSG:3395",
    threshold: float | None = None,
) -> pd.DataFrame:
    """
    For every timestamp, assign the nearest station gradient to each
    polygon centroid.

    Result
    
    DataFrame: Centroids with a new column 'gradient_value'.
    """
    results: list[pd.DataFrame] = []

    for tstamp, grp_sta in df_grad.groupby("valid"):
        grp_cent = df_centroids[df_centroids["valid"] == tstamp]
        if grp_cent.empty:
            continue

        gdf_sta = gpd.GeoDataFrame(
            grp_sta,
            geometry=gpd.points_from_xy(grp_sta["x"], grp_sta["y"]),
            crs=crs,
        )
        gdf_cent = gpd.GeoDataFrame(
            grp_cent,
            geometry=gpd.points_from_xy(grp_cent["x"], grp_cent["y"]),
            crs=crs,
        )

        joined = gpd.sjoin_nearest(
            gdf_cent,
            gdf_sta[["gradient_value", "geometry"]],
            how="left",
            distance_col="dist",
        )

        if threshold is not None:
            joined.loc[joined["dist"] > threshold, "gradient_value"] = 0

        joined["gradient_value"] = joined["gradient_value"].fillna(0)
        results.append(joined.drop(columns=["geometry", "dist"]))

    return pd.concat(results, ignore_index=True) if results else pd.DataFrame()
