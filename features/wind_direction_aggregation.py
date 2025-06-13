drct_base_path = " "
sknt_raw_path  = " "
sknt_agg_path  = " "
output_dir     = " "
os.makedirs(output_dir, exist_ok=True)

years = [2021, 2022]

for year in years:
    # read aggregated csv
    agg_sknt_file = os.path.join(sknt_agg_path, f"agg_sknt_{year}.csv")
    if not os.path.isfile(agg_sknt_file):
        continue

    df_sknt_agg = pd.read_csv(agg_sknt_file, parse_dates=['valid'])
    # rename columns to 'sknt_max', 'valid_hour':
    df_sknt_agg.rename(columns={'sknt': 'sknt_max'}, inplace=True, errors='ignore')
    df_sknt_agg.rename(columns={'valid': 'valid_hour'}, inplace=True, errors='ignore')

    # read sknt
    pattern_sknt_raw = os.path.join(sknt_raw_path, f"cleaned_sknt_{year}", "*.csv")
    sknt_files = glob.glob(pattern_sknt_raw)
    if not sknt_files:
        print(f"No raw SKNT files found for {year}") # troubleshooting
        continue

    # concatenate two dataframes
    df_sknt_list = []
    for f in sknt_files:
        tmp = pd.read_csv(f, parse_dates=['valid'])
        df_sknt_list.append(tmp)
    df_sknt_raw = pd.concat(df_sknt_list, ignore_index=True).drop_duplicates()

    df_sknt_raw.dropna(subset=['valid'], inplace=True)

    # create valid_hour
    df_sknt_raw['valid_hour'] = df_sknt_raw['valid'].dt.floor('1h')

    # check if the column ('station','valid','lon','lat','sknt','valid_hour') is present in initial dataframe
    needed_cols = {'station','valid','lon','lat','sknt','valid_hour'}
    missing = needed_cols - set(df_sknt_raw.columns)

    # merge with hourly aggregated sknt_max
    df_merged = pd.merge(
        df_sknt_raw,
        df_sknt_agg[['station','valid_hour','sknt_max']],
        on=['station','valid_hour'],
        how='inner'
    )

    # Pick up lines that have wind speed = max
    mask_max = (df_merged['sknt'] == df_merged['sknt_max'])
    df_max_sub = df_merged[mask_max].copy()

   # read raw dataframe drct
    pattern_drct = os.path.join(drct_base_path, f"cleaned_drct_{year}", "*.csv")
    drct_files = glob.glob(pattern_drct)
    if not drct_files:
        continue
    # concatenate with drct, read csv, drop raws without 'valid' becasue it is a key for merge
    df_drct_list = []
    for f in drct_files:
        tmp = pd.read_csv(f, parse_dates=['valid'])
        df_drct_list.append(tmp)
    df_drct_raw = pd.concat(df_drct_list, ignore_index=True).drop_duplicates()
    df_drct_raw.dropna(subset=['valid'], inplace=True)

    # merge sub-hourly max with drct
    df_final = pd.merge(
        df_max_sub,
        df_drct_raw[['station','valid','drct']],
        on=['station','valid'],
        how='inner'
    )

    # calculate u, v components
    df_final['speed_m_s'] = df_final['sknt_max'] * 0.514444
    df_final['theta_rad'] = np.radians(df_final['drct'])
    df_final['u'] = -df_final['speed_m_s'] * np.sin(df_final['theta_rad'])
    df_final['v'] = -df_final['speed_m_s'] * np.cos(df_final['theta_rad'])
    df_final['u'] = df_final['u'].apply(lambda x: 0.0 if abs(x) < 1e-9 else x)
    df_final['v'] = df_final['v'].apply(lambda x: 0.0 if abs(x) < 1e-9 else x)

    # choose columns to final csv
    df_final.sort_values(['station','valid_hour','valid'], inplace=True)


    out_cols = [
        'station',
        'lon','lat',         # from raw sknt
        'valid_hour',        # created from df_sknt_raw
        'valid',             # exact sub-hour
        'sknt_max',          # from aggregated sknt
        'drct',              # from raw drkt
        'u','v'              # computed components on sknt_max and drct
    ]
    # check if they are present in df final
    missing_out = set(out_cols) - set(df_final.columns)
    if missing_out:
        print(f"requested columns are missing: {missing_out}")

    df_output = df_final[out_cols].copy()

    out_file = os.path.join(output_dir, f"agg_drct_{year}.csv")
    df_output.to_csv(out_file, index=False, date_format='%Y-%m-%d %H:%M:%S')

    print(f"ok Year {year} aggregated direction saved to {out_file}")

print("done!")
