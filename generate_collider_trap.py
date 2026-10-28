import numpy as np
import pandas as pd
import os
from scipy.special import expit

def generate_collider_trap(n=10000, random_state=42):
    np.random.seed(random_state)
    
    # Structural coefficients
    alpha = 1.0
    beta = 2.0  # True ATE
    gamma = 1.5
    delta = 1.0
    
    # Missingness coefficients
    w1 = 2.0
    w2 = 2.0
    
    W_C = np.random.normal(0, 1, n)
    W_Z = np.random.normal(0, 1, n)
    
    W_X = alpha * W_C + np.random.normal(0, 0.5, n)
    W_B = delta * W_Z + np.random.normal(0, 0.5, n)
    
    Y = beta * W_X + gamma * W_C + np.random.normal(0, 0.5, n)
    
    # Missingness Collider P(R_x = 1)
    prob_missing = expit(w1 * W_C + w2 * W_B - 1.0)
    RW_X = np.random.binomial(1, prob_missing)
    
    df_complete = pd.DataFrame({
        "W_C": W_C,
        "W_Z": W_Z,
        "W_X": W_X,
        "W_B": W_B,
        "Y": Y,
        "RW_X": RW_X
    })
    
    df_missing = df_complete.copy()
    df_missing.loc[df_missing["RW_X"] == 1, "W_X"] = np.nan
    
    return df_complete, df_missing, beta

def main():
    sizes = [2000, 5000, 10000]
    out_dir_complete = "dataframe/ArtificialData_complete"
    out_dir_missing = "dataframe/ArtificialData"
    
    os.makedirs(out_dir_complete, exist_ok=True)
    os.makedirs(out_dir_missing, exist_ok=True)
    
    for size in sizes:
        df_complete, df_missing, true_ate = generate_collider_trap(n=size)
        
        complete_path = os.path.join(out_dir_complete, f"complete_data_collider_trap_{size}.csv")
        missing_path = os.path.join(out_dir_missing, f"data_collider_trap_{size}.csv")
        
        df_complete.to_csv(complete_path, index=False)
        df_missing.to_csv(missing_path, index=False)
        
        print(f"Generated size {size} - True ATE: {true_ate}")
        print(f" Saved complete to {complete_path}")
        print(f" Saved missing to {missing_path}")

if __name__ == "__main__":
    main()
