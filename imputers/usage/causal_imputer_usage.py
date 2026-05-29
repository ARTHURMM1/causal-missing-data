from ..causal_imputer import CausalImputer

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error

# ============================================================
# DAG structure
# ============================================================

graph = {

    # W nodes
    "W1": ["C1", "C2"],
    "W2": ["C1", "C3"],
    "W3": ["C2", "C4"],

    # Treatment
    "X": [
        "C1", "C2",
        "W1", "W2",
    ],

    # Outcome
    "Y": [
        "X",
        "W1",
        "W2",
        "W3"
    ],

    # Missingness
    "RW1": ["C1", "C2", "C3"],
    "RW2": ["C1", "C2", "C3"],
    "RW3": ["C1", "C2", "C3"],
}

# ============================================================
# Load incomplete data
# ============================================================

data = pd.read_csv(
    "dataframe/ArtificialData/data_mar_baseline_10000.csv"
)

# ============================================================
# Load ground truth
# ============================================================

gt = pd.read_csv(
    "dataframe/ArtificialData_complete/complete_data_mar_baseline_10000.csv"
)

# ============================================================
# Fit imputer
# ============================================================

imputer = CausalImputer(
    graph=graph,
    m=20
)

imputer.fit(data)

# ============================================================
# Generate imputations
# ============================================================

datasets = imputer.transform(data)

# ============================================================
# DR weights
# ============================================================

weights = imputer.get_dr_weights(data)

print("\n=== DR WEIGHTS ===")
print(weights.head())

# ============================================================
# Pooled ATE
# ============================================================

pooled_ate = imputer.pooled_ate(
    datasets
)

print("\n=== ATE ===")
print("Pooled ATE:", pooled_ate)

# ============================================================
# Ground truth ATE
# ============================================================

gt_ate = (
    gt[gt["X"] == 1]["Y"].mean()
    -
    gt[gt["X"] == 0]["Y"].mean()
)

print("Ground Truth ATE:", gt_ate)

print(
    "ATE Bias:",
    abs(pooled_ate - gt_ate)
)

# ============================================================
# Compare imputed vs original
# ============================================================

print("\n=== IMPUTATION QUALITY ===")

first_dataset = datasets[0]

for w in ["W1", "W2", "W3"]:

    # only evaluate original missing positions
    missing_mask = data[w].isna()

    imputed_values = first_dataset.loc[
        missing_mask,
        w
    ]

    true_values = gt.loc[
        missing_mask,
        w
    ]

    rmse = np.sqrt(
        mean_squared_error(
            true_values,
            imputed_values
        )
    )

    mae = np.mean(
        np.abs(
            true_values - imputed_values
        )
    )

    print(f"\n{w}")
    print("Missing values:", missing_mask.sum())
    print("RMSE:", rmse)
    print("MAE:", mae)

# ============================================================
# Compare means
# ============================================================

print("\n=== DISTRIBUTION COMPARISON ===")

for w in ["W1", "W2", "W3"]:

    original_mean = gt[w].mean()

    imputed_mean = first_dataset[w].mean()

    print(f"\n{w}")
    print("Original mean:", original_mean)
    print("Imputed mean:", imputed_mean)

# ============================================================
# Check if missing values remain
# ============================================================

print("\n=== REMAINING NaNs ===")

print(
    first_dataset[
        ["W1", "W2", "W3"]
    ].isna().sum()
)

# ============================================================
# Compare imputations
# ============================================================

print("\n=== MULTIPLE IMPUTATION CHECK ===")

print(
    datasets[0][["W1"]].head()
)

print(
    datasets[1][["W1"]].head()
)