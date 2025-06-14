# compute gradient values between stations for relative humidity
def compute_local_gradient_min_dist( 
    df,
    param_name,
    max_radius=1_000_000,
    scale_factor=1.0
):
    """
        Steps:
      1) Group by 'valid' (timestamp).
      2) Build a KD-tree for each group.
      3) For each station, query the tree to find neighbors within max_radius (or k+1 neighbors).
      4) Exclude the station itself (distance=0).
      5) Take the neighbor with the minimal distance d_min among those that remain.
      6) Compute gradient = |z_i - z_j| / d_min.
      7) Multiply by scale_factor for normalization).
    """
    df = df.copy()
    df["gradient_value"] = 0.0

    # Group by timestamp
    grouped = df.groupby("valid", sort=False)
    results = []

    for valid_time, group in grouped:
        # If there's only one station in this group, gradient is 0
        if len(group) < 2:
            results.append(group)
            continue

        # Build KD-tree
        X = group[["x", "y"]].values
        Z = group[param_name].values
        tree = cKDTree(X)

        # Array to store local gradients
        local_grad = np.zeros(len(group), dtype=float)

        for i in range(len(group)):
            xi = X[i]
            zi = Z[i]

            # Finding indexes of all neighbours in the radius
            neighbor_idxs = tree.query_ball_point(xi, r=max_radius)

            # Exclude the station itself
            if i in neighbor_idxs:
                neighbor_idxs.remove(i)

            if not neighbor_idxs:
                # If there are no neighbours in the radius, gradient = 0
                local_grad[i] = 0.0
                continue

            # Compute distances to all indexes
            dists = [np.linalg.norm(xi - X[idx]) for idx in neighbor_idxs]
            # Finding index of the nearest distance
            min_idx = np.argmin(dists)
            d_min = dists[min_idx]
            j = neighbor_idxs[min_idx]  # index of the neighbour with the nearest distance

            if d_min == 0:
                # to avoid devideing by zero
                local_grad[i] = 0.0
            else:
                zj = Z[j]
                grad_val = abs(zi - zj) / d_min
                local_grad[i] = grad_val

        group = group.copy()
        group["gradient_value"] = local_grad * scale_factor
        results.append(group)

    df_with_grad = pd.concat(results, ignore_index=True)
    return df_with_grad
