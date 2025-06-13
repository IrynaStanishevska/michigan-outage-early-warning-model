
raw_data_path = ''
processed_data_path = '
# find all raw datasets
for csv_file in glob.iglob(os.path.join(raw_data_path, '**', '*.csv'), recursive=True):
    # get relative path 
    rel_path = os.path.relpath(csv_file, raw_data_path)

    # split folders and names
    parts = rel_path.split(os.sep)  

   # replaced _raw prefix with _cleaned
    new_parts = []
    for part in parts:
        if part.startswith('raw_'):
            new_parts.append(part.replace('raw_', 'cleaned_'))
        else:
            new_parts.append(part)

    # join into path
    out_rel_path = os.path.join(*new_parts)

    out_path = os.path.join(processed_data_path, out_rel_path)

    # create a directory if does not exist
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # skip 5 technical raws
    df = pd.read_csv(csv_file, skiprows=5)

    # for missing data change M to NA 
    df.replace("M", pd.NA, inplace=True)

    # convert valid to datetime
    df['valid'] = pd.to_datetime(df['valid'], errors='coerce')

    df.drop_duplicates(inplace=True)

    # save to csv
    df.to_csv(out_path, index=False, date_format='%Y-%m-%d %H:%M:%S')

    print(f"processed: {csv_file} -> {out_path}")
