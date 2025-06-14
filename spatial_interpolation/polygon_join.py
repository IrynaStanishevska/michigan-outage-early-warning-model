# polygon_join.py
import pandas as pd
import geopandas as gpd

def spatial_point_in_polygon_join(
    df_stations: pd.DataFrame,
    gdf_polygons: gpd.GeoDataFrame,
    crs: str = "ESRI:102121"
) -> pd.DataFrame:
    """
    1. Convert stations to GeoDataFrame.
    2. Spatial join (point‑within‑polygon).
    3. For each polygon & hour choose max(param) in area limited by threshold
    4. Build a full matrix
    5. Attach polygon centroids (x_c, y_c) 
    """
    # points → GeoDataFrame
    gdf_sta = gpd.GeoDataFrame(
        df_stations.copy(),
        geometry=gpd.points_from_xy(df_stations["x"], df_stations["y"]),
        crs=crs,
    )

    # unify CRS
    gdf_polygons = gdf_polygons.to_crs(crs)

    #  point‑in‑polygon
    gdf_join = gpd.sjoin(
        gdf_sta, gdf_polygons, how="left", predicate="within"
    )

    # max flag per polygon & hour
    df_max = (
        gdf_join.groupby(["Name", "valid"], as_index=False)["ts_flag"]
        .max()
    )

    # all polygons × all hours
    df_all = (
        pd.MultiIndex.from_product(
            [gdf_polygons["Name"].unique(), df_stations["valid"].unique()],
            names=["Name", "valid"],
        )
        .to_frame(index=False)
    )

    # left join & fill NA → 0
    df_merge = (
        df_all.merge(df_max, on=["Name", "valid"], how="left")
        .fillna({"ts_flag": 0})
    )

    # append centroids
    gdf_polygons = gdf_polygons.copy()
    gdf_polygons["centroid"] = gdf_polygons.geometry.centroid
    gdf_polygons["x_c"] = gdf_polygons.centroid.x
    gdf_polygons["y_c"] = gdf_polygons.centroid.y

    return df_merge.merge(
        gdf_polygons[["Name", "x_c", "y_c"]], on="Name", how="left"
    )
  from polygon_join import spatial_point_in_polygon_join
