import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

def compute_local_gradient_min_dist(
    df: pd.DataFrame,
    param_name: str,
    max_radius: float = 1_000_000,
    scale_factor: float = 1.0,
) -> pd.DataFrame:
    """
    Local gradient indicator for relative humidity

    For each timestamp:
        1. build KD‑tree on station coordinates (x, y);
        2. find the nearest neighbour within `max_radius`;
        3. gradient = |z_i − z_j| / d_min;
        4. result is scaled by `scale_factor`.
    """
    df = df.copy()
    df["gradient_value"] = 0.0
    results = []

    # loop over each hour (or whatever 'valid' is)
    for _, group in df.groupby("valid", sort=False):
        if len(group) < 2:                # only one station → gradient = 0
            results.append(group)
            continue

        X = group[["x", "y"]].values
        Z = group[param_name].values
        tree = cKDTree(X)
        local_grad = np.zeros(len(group))

        for i, (xi, zi) in enumerate(zip(X, Z)):
            idxs = tree.query_ball_point(xi, r=max_radius)
            if i in idxs:
                idxs.remove(i)
            if not idxs:                  # no neighbours in radius
                continue
            dists = np.linalg.norm(X[idxs] - xi, axis=1)
            j = idxs[np.argmin(dists)]    # nearest neighbour
            d_min = dists.min()
            if d_min != 0:
                local_grad[i] = abs(zi - Z[j]) / d_min

        group = group.copy()
        group["gradient_value"] = local_grad * scale_factor
        results.append(group)

    return pd.concat(results, ignore_index=True)
