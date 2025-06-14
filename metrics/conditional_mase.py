def conditional_mase(y_true, y_pred, peak_thresh=50_000,
                     delta_hours=0, m=24):
  
   """
   Conditional MASE: computes Mean Absolute Scaled Error but restricts evaluation to errors only on high peak values (>= 50,000).
   And includes delta hours windows around the peak

   Parameters:
   y_true: actual target value
   y_pred: predict
   peak_thresh: threshold for peak
   delta_hours: time windows
   m: seasonal lag for naive forecast
   """
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    n = len(y_true)
    # 1. identify peaks
    mask = y_true >= peak_thresh
    # 2. mask to include delta hours around the peak
    if delta_hours > 0 and mask.any():
        idx = np.where(mask)[0]
        for i in idx:
            mask[max(0, i-delta_hours):min(n, i+delta_hours+1)] = True
    # 3. if no peak points are found, there is nothing to evaluate, then return NaN to indicate undefined metrics
    if mask.sum() == 0:
        return np.nan
    # compute conditional mae only peaks and windows    
    mae_cond = np.abs(y_true[mask] - y_pred[mask]).mean()
    #compute naive mae using seasonal lag
    naive = np.abs(y_true[m:] - y_true[:-m]).mean()
    return mae_cond / naive
