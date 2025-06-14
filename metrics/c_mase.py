# conditional MASE
import numpy as np

def conditional_mase(
    y_true,
    y_pred,
    peak_thresh: float = 50_000,
    delta_hours: int = 0,
    m: int = 24,
) -> float:
    """
    Conditional Mean Absolute Scaled Error (MASE).

    Computes MASE only on high peaks
    plus ± ``delta_hours`` window around each peak.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if y_true.shape != y_pred.shape:
        raise ValueError("y_true and y_pred must have the same shape")

    n = len(y_true)

    # 1. Identify peak positions
    mask = y_true >= peak_thresh

    # 2. Expand mask by ± delta_hours
    if delta_hours > 0 and mask.any():
        idx = np.where(mask)[0]
        for i in idx:
            mask[max(0, i - delta_hours): min(n, i + delta_hours + 1)] = True

    # 3. If no peaks (or windows) → metric undefined
    if mask.sum() == 0:
        return np.nan

    # 4. Mean absolute error on the selected subset
    mae_conditional = np.abs(y_true[mask] - y_pred[mask]).mean()

    # 5. Naïve seasonal MAE (denominator)
    if n <= m:
        return np.nan  # cannot compute seasonal naive
    naive_mae = np.abs(y_true[m:] - y_true[:-m]).mean()
    if naive_mae == 0:
        return np.nan  # avoid division by zero

    return mae_conditional / naive_mae
