processed_data_path = ""
output_data_path = ""

# 1. aggregation
aggregation_map = {
    'tmpf': 'mean',  # mean for temperature
    'relh': 'mean',  # mean for humidity
    'dwpf': 'mean',  # mean for dew point
    'p01i': 'max',   # max for precipitation
    'alti': 'mean',  # mean for alti pressure
    'mslp': 'mean',  # mean for sea level pressure
    'gust': 'max',   # max for gust
    'sknt': 'max'    # max for wind speed
}

# 2. fill missing values
fillna_methods = {
    'tempf': 'ffill',  # forward fill for temperature
    'relh': 'ffill',   # forward fill for humidity
    'dwpf': 'ffill',   # forward fill for dew point
    'p01i': 0,         # 0 is used for missing values in precipitation dataset
    'alti': 'ffill',   # forward fill for alti pressure
    'mslp': 'ffill',   # forward fill for  sea level pressure
    'gust': None,      # keep NaN
    'sknt': 'ffill'   # forward fill for wind speed
}


years = [2021, 2022]

for column, aggfunc in aggregation_map.items():
    for year in years:
        pattern = os.path.join(
            processed_data_path,
            f"cleaned_{column}",
            f"cleaned_{column}_{year}",
            "*.csv"
        )
        file_list = glob.glob(pattern) # get the list of csv matching names

       # assemble all parts
        df_list = []
        for csv_file in file_list:
            df = pd.read_csv(csv_file)

            df['valid'] = pd.to_datetime(df['valid'], errors='coerce')
            df.dropna(subset=['valid'], inplace=True)
            df_list.append(df)

        # 3. concatenate
        df_all = pd.concat(df_list, ignore_index=True).drop_duplicates()

        grouped = df_all.groupby(['station', 'lon', 'lat'], dropna=False)
        group_dfs = []


        for (st, lon, lat), subdf in grouped:
            subdf = subdf.sort_values('valid').set_index('valid') # sort by time, set valid as index

            subdf_hourly = subdf[column].resample('1h').agg(aggfunc)

            subdf_hourly = subdf_hourly.to_frame(name=column) # parameter as a column name

           # 5. fill NaN according to fillna_methods
            fill_method = fillna_methods.get(column, None)
            if fill_method is None:
                pass # do not fill NaN
            elif fill_method == 'ffill':
                subdf_hourly[column] = subdf_hourly[column].ffill(limit=1)
            elif isinstance(fill_method, (int, float)):
                subdf_hourly[column] = subdf_hourly[column].fillna(fill_method)


            subdf_hourly.dropna(subset=[column], inplace=True) # drop any remaining NaN

            # 6. return station, lon, lat
            subdf_hourly['station'] = st
            subdf_hourly['lon'] = lon
            subdf_hourly['lat'] = lat

            subdf_hourly.reset_index(inplace=True)  # new 'valid' column

            group_dfs.append(subdf_hourly)

        df_result = pd.concat(group_dfs, ignore_index=True)

        df_result.sort_values(by=['station', 'valid'], inplace=True)

        df_result = df_result[['valid', 'station', 'lon', 'lat', column]] # define the column order

        out_dir = os.path.join(output_data_path, f"agg_{column}") # save to csv
        os.makedirs(out_dir, exist_ok=True)

        out_file = os.path.join(out_dir, f"agg_{column}_{year}.csv")
        df_result.to_csv(out_file, index=False, date_format='%Y-%m-%d %H:%M:%S')

        print(f"OK Aggregated '{column}' for {year} by {aggfunc}, saved -> {out_file}")
