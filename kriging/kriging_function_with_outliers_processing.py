import numpy as np
import pandas as pd
from pykrige.uk import UniversalKriging
from skgstat import Variogram
import geopandas as gpd

# Hour-by-hour kriging foer a single year
def kriging_one_year(df_prep, df_grid, param_name, maxlag=250_000):
    """
    Build an hourly Universal‑Kriging field for an entire year
    """
    # Unique hourly time stamps
    unique_hours = np.sort(df_prep['valid'].unique())
    all_predictions = []

    for ts in unique_hours:
        # Select data for one specific hour
        df_hour = df_prep[df_prep['valid'] == ts]
        x_train = df_hour['x'].values
        y_train = df_hour['y'].values
        z_train = df_hour[param_name].values
       
        # skip if there are too few stations
        if len(df_hour) < 3:  # at least three stations are required
            continue  

           # case 1: all stations report the same value
        if np.unique(z_train).size == 1:
          # Fill all points with the same value
            z_pred = np.full(len(df_grid), z_train[0]) # flat field
            ss_pred = np.zeros(len(df_grid)) # zero variance
          # case 2: standard workflow – fit variogram and run UK
        else:
          # 1) Empirical variogram  (scikit‑gstat)
            vario = Variogram(
                coordinates=np.column_stack([x_train, y_train]),
                values=z_train,
                model='spherical',
                drift_terms=['regional_linear'],
                maxlag=maxlag,
            )
            rdesc   = vario.describe() # sill, range, nugget
            # 2. Universal Kriging (PyKrige) using fitted parameters
            uk = UniversalKriging(
                x_train, y_train, z_train,
                variogram_model='spherical',
                variogram_parameters=[
                    rdesc['sill'],
                    rdesc['effective_range'],
                    rdesc['nugget']
                ],
                drift_terms=['regional_linear']
            )
             # 3) Predict
            z_pred, ss_pred = uk.execute(
                style='points',
                xpoints=df_grid['x'].values,
                ypoints=df_grid['y'].values
            )
        # DataFrame with results
        df_res = pd.DataFrame({
            'valid': [ts] * len(df_grid),
            'x': df_grid['x'].values,
            'y': df_grid['y'].values,
            f'pred_{param_name}': z_pred,
            'variance': ss_pred
        })
        all_predictions.append(df_res)
    # concatenate all predictions to one table
    return pd.concat(all_predictions, ignore_index=True)

   #--------Postprocessing with Spatial Joint for Outliers--------
   # Replaced kriging estimates with observed extremes
    def spatial_joint_with_outliers(
    """
    for each outlier, overwrite the nearest kriging point (within threshold meters) by the observed value. 
    If several outliers refer to the same point, use the highest value (risk-aware)
    """
    df_krig: pd.DataFrame,
    df_outliers: pd.DataFrame,
    param_name: str = 'dwpf',
    crs: str = 'EPSG:3395',
    threshold: float = 200_000
) -> pd.DataFrame:
    pred_col = f"pred_{param_name}"  # for instance 'pred_sknt'

    # Convert df_krig to GeoDataFrame
    gdf_krig = gpd.GeoDataFrame(
        df_krig.copy(),
        geometry=gpd.points_from_xy(df_krig['x'], df_krig['y']),
        crs=crs
    )

    #  df_outliers into GeoDataFrame
    gdf_outliers = gpd.GeoDataFrame(
        df_outliers.copy(),
        geometry=gpd.points_from_xy(df_outliers['x'], df_outliers['y']),
        crs=crs
    )

    # Temporary columns for overridden values / variances
    gdf_krig['override_value'] = np.nan
    gdf_krig['override_var'] = np.nan

    # unique timestamp in df_krig 
    all_valids_krig = gdf_krig['valid'].unique()
    # Loop through each hour to preserve the full temporal resolution
    for dt in sorted(all_valids_krig):
        # select all kriging points for the current hour 
        mask_krig_dt = (gdf_krig['valid'] == dt) # kriging points
        gdf_krig_dt = gdf_krig[mask_krig_dt]  # outlier stations
        if gdf_krig_dt.empty:
            continue  # no kriging points for this hour

        # select outliers on the same date/hour 
        gdf_out_dt = gdf_outliers[gdf_outliers['valid'] == dt]
        if gdf_out_dt.empty:
            # if there are no outliers - > do not override -> ничего не переопределяем
            continue

         # Nearest‑neighbour join (each station → closest grid node)
         joined = gpd.sjoin_nearest(
            gdf_out_dt,
            gdf_krig_dt,
            how='left',
            distance_col='dist'
        )

        # Keep only station‑node pairs closer than threshold
        joined = joined[joined['dist'] <= threshold]

        # Overwrite kriging prediction with observed value
        override_map = {}
        for _, row in joined.iterrows():
            idx_right = row['index_right']  # node index inside gdf_krig
            real_value = row[param_name]    # measured extreme

            if idx_right not in override_map:
                override_map[idx_right] = real_value
            else:
                override_map[idx_right] = max(override_map[idx_right], real_value)

        # apply override_map
        for idx_right, val in override_map.items():
            gdf_krig.loc[idx_right, 'override_value'] = val
            gdf_krig.loc[idx_right, 'override_var'] = 0  

    # Replace pred_sknt and variance where the override_value is available 
    def apply_override_value(row):
        if not pd.isna(row['override_value']):
            return row['override_value']
        return row[pred_col]

    def apply_override_var(row):
        if not pd.isna(row['override_var']):
            return row['override_var']
        return row['variance']
      
    # Combine overridden cells with original predictions
    gdf_krig[pred_col] = gdf_krig.apply(apply_override_value, axis=1)
    gdf_krig['variance'] = gdf_krig.apply(apply_override_var, axis=1)

    # Drop temporal columns overrive and geometry 
    gdf_krig.drop(columns=['override_value', 'override_var', 'geometry'], inplace=True)

    return gdf_krig
