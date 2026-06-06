import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from imputers.baseline import MeanModeImputer, MiceForestImputer
from imputers.causal_imputer import CausalImputer

def evaluate_pima():
    print("--------------------------------------------------")
    print("Evaluating Pima Indians Dataset (Real World)")
    print("--------------------------------------------------")
    df = pd.read_csv("dataframe/diabetes.csv")
    
    cols_to_nan = ["Insulin", "SkinThickness", "BloodPressure", "BMI", "Glucose"]
    for col in cols_to_nan:
        df[col] = df[col].replace(0, np.nan)
        
    w_cols_map = {
        "Glucose": "W_Glucose",
        "BMI": "W_BMI",
        "BloodPressure": "W_BloodPressure",
        "SkinThickness": "W_SkinThickness",
        "Insulin": "W_Insulin",
        "Age": "W_Age",
        "Pregnancies": "W_Pregnancies",
        "DiabetesPedigreeFunction": "W_DiabetesPedigreeFunction"
    }
    df = df.rename(columns=w_cols_map)
    df = df.rename(columns={"Outcome": "Y"})
    
    for col in cols_to_nan:
        w_col = w_cols_map[col]
        df[f"RW_{col}"] = df[w_col].isna().astype(int)

    graph = {
        "W_Glucose": [],
        "W_BMI": [],
        "W_BloodPressure": [],
        "W_SkinThickness": [],
        "W_Insulin": [],
        "W_Age": [],
        "W_Pregnancies": [],
        "W_DiabetesPedigreeFunction": [],
        "Y": ["W_Glucose", "W_BMI", "W_BloodPressure", "W_SkinThickness", "W_Insulin", "W_Age", "W_Pregnancies", "W_DiabetesPedigreeFunction"],
        "RW_Insulin": ["W_Glucose", "W_Age"],
        "RW_SkinThickness": ["W_BMI", "W_Age"],
        "RW_BloodPressure": ["W_Age"],
        "RW_BMI": [],
        "RW_Glucose": []
    }
    
    w_columns = list(w_cols_map.values())
    
    imputers = {
        "MeanMode": MeanModeImputer(),
        "MiceForest": MiceForestImputer(datasets=5, iterations=5, random_state=42),
        "CausalImputer": CausalImputer(graph=graph, m=5, estimator=RandomForestRegressor(n_estimators=20, random_state=42))
    }
    
    results = {}
    for name, imputer in imputers.items():
        print(f"Running {name}... (this may take some time for complex imputers)")
        try:
            # We directly pass the dataframe which now has np.nan for natural missing values (0s)
            imputed_datasets = imputer.fit_transform(df)
            avg_imputed_df = imputed_datasets[0].copy()
            for i in range(1, len(imputed_datasets)):
                avg_imputed_df[w_columns] += imputed_datasets[i][w_columns]
            avg_imputed_df[w_columns] /= len(imputed_datasets)
            
            X = avg_imputed_df[w_columns]
            y = avg_imputed_df["Y"]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            clf = RandomForestClassifier(random_state=42)
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            y_prob = clf.predict_proba(X_test)[:, 1]
            f1 = f1_score(y_test, y_pred)
            auroc = roc_auc_score(y_test, y_prob)
            results[name] = {"F1": f1, "AUROC": auroc}
        except Exception as e:
            print(f"Error with {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = {"F1": None, "AUROC": None}
            
    return results

def evaluate_synthetic(dataset_path, gt_path, name):
    print("--------------------------------------------------")
    print(f"Evaluating Synthetic Dataset: {name}")
    print("--------------------------------------------------")
    data = pd.read_csv(dataset_path)
    gt = pd.read_csv(gt_path)
    
    graph = {
        "W1": ["C1", "C2"],
        "W2": ["C1", "C3"],
        "W3": ["C2", "C4"],
        "X": ["C1", "C2", "W1", "W2"],
        "Y": ["X", "W1", "W2", "W3"],
        "RW1": ["C1", "C2", "C3"],
        "RW2": ["C1", "C2", "C3"],
        "RW3": ["C1", "C2", "C3"],
    }
    
    # Check if there are other columns not explicitly listed, we just give them empty list
    for c in data.columns:
        if c not in graph:
            graph[c] = []

    from sklearn.linear_model import LinearRegression
    
    # Calculate Ground Truth ATE using Linear Regression
    features = [c for c in gt.columns if c not in ["Y", "RW1", "RW2", "RW3", "Z1", "Z2", "C5"]] 
    # Use features that are relevant, e.g. W1, W2, W3, C1, C2, C3, C4, X
    features = ["X", "W1", "W2", "W3", "C1", "C2", "C3", "C4"]
    
    lr_gt = LinearRegression()
    lr_gt.fit(gt[features], gt["Y"])
    gt_ate = lr_gt.coef_[0] # coefficient for X
    
    imputers = {
        "MeanMode": MeanModeImputer(),
        "MiceForest": MiceForestImputer(datasets=5, iterations=5, random_state=42),
        "CausalImputer": CausalImputer(graph=graph, m=5, estimator=RandomForestRegressor(n_estimators=20, random_state=42))
    }
    
    results = {}
    for imp_name, imputer in imputers.items():
        print(f"Running {imp_name}... (this may take some time for complex imputers)")
        try:
            imputed_datasets = imputer.fit_transform(data)
            
            # Calculate metrics
            ates = []
            w_cols = ["W1", "W2", "W3"]
            
            for df_imp in imputed_datasets:
                lr_imp = LinearRegression()
                lr_imp.fit(df_imp[features], df_imp["Y"])
                ates.append(lr_imp.coef_[0])
                
            pooled_ate = np.mean(ates)
            ate_bias = np.abs(pooled_ate - gt_ate)
            
            # For reconstruction, we can average datasets or just pick first. Let's average them.
            avg_imputed = imputed_datasets[0].copy()
            for i in range(1, len(imputed_datasets)):
                for w in w_cols:
                    avg_imputed[w] += imputed_datasets[i][w]
            for w in w_cols:
                avg_imputed[w] /= len(imputed_datasets)
                
            rmse_list = []
            mae_list = []
            for w in w_cols:
                missing_mask = data[w].isna()
                if missing_mask.sum() > 0:
                    true_vals = gt.loc[missing_mask, w]
                    imp_vals = avg_imputed.loc[missing_mask, w]
                    rmse_list.append(np.sqrt(mean_squared_error(true_vals, imp_vals)))
                    mae_list.append(mean_absolute_error(true_vals, imp_vals))
                    
            mean_rmse = np.mean(rmse_list) if rmse_list else 0
            mean_mae = np.mean(mae_list) if mae_list else 0
            
            results[imp_name] = {"MAE": mean_mae, "RMSE": mean_rmse, "ATE_Bias": ate_bias}
        except Exception as e:
            print(f"Error with {imp_name}: {e}")
            import traceback
            traceback.print_exc()
            results[imp_name] = {"MAE": None, "RMSE": None, "ATE_Bias": None}
            
    return results


def evaluate_collider_trap(dataset_path, gt_path, name):
    print("--------------------------------------------------")
    print(f"Evaluating Synthetic Dataset: {name}")
    print("--------------------------------------------------")
    df = pd.read_csv(dataset_path)
    gt = pd.read_csv(gt_path)
    true_ate = 2.0
    
    graph = {
        "W_X": ["W_C"],
        "Y": ["W_X", "W_C"],
        "W_B": ["W_Z"],
        "RW_X": ["W_C", "W_B"],
        "W_C": [],
        "W_Z": []
    }
    
    imputers = {
        "MeanMode": MeanModeImputer(),
        "MiceForest": MiceForestImputer(datasets=5, iterations=5, random_state=42),
        "CausalImputer": CausalImputer(graph=graph, m=5, estimator=RandomForestRegressor(n_estimators=10, max_depth=10, random_state=42))
    }
    
    results = {}
    from sklearn.linear_model import LinearRegression
    for imp_name, imputer in imputers.items():
        print(f"Running {imp_name}... (this may take some time for complex imputers)")
        try:
            imputed_datasets = imputer.fit_transform(df)
            
            ates = []
            for imp_df in imputed_datasets:
                X_features = imp_df[["W_X", "W_C"]]
                y_target = imp_df["Y"]
                lr = LinearRegression()
                lr.fit(X_features, y_target)
                ates.append(lr.coef_[0])
                
            pooled_ate = np.mean(ates)
            ate_bias = np.abs(pooled_ate - true_ate)
            
            avg_imputed = imputed_datasets[0].copy()
            for i in range(1, len(imputed_datasets)):
                avg_imputed["W_X"] += imputed_datasets[i]["W_X"]
            avg_imputed["W_X"] /= len(imputed_datasets)
            
            missing_mask = df["W_X"].isna()
            if missing_mask.sum() > 0:
                true_vals = gt.loc[missing_mask, "W_X"]
                imp_vals = avg_imputed.loc[missing_mask, "W_X"]
                rmse = np.sqrt(mean_squared_error(true_vals, imp_vals))
                mae = mean_absolute_error(true_vals, imp_vals)
            else:
                rmse = 0.0
                mae = 0.0
            
            results[imp_name] = {"MAE": mae, "RMSE": rmse, "ATE_Bias": ate_bias}
        except Exception as e:
            print(f"Error with {imp_name}: {e}")
            results[imp_name] = {"MAE": None, "RMSE": None, "ATE_Bias": None}
            
    return results

def main():
    final_results = {}
    
    # 1. Pima Indians
    pima_res = evaluate_pima()
    final_results["Pima Indians"] = pima_res
    
    # 2. MCAR 10000
    mcar_res = evaluate_synthetic(
        "dataframe/ArtificialData/data_mcar_10000.csv",
        "dataframe/ArtificialData_complete/complete_data_mcar_10000.csv",
        "MCAR_10000"
    )
    final_results["MCAR_10000"] = mcar_res
    
    # 3. MAR 10000
    mar_res = evaluate_synthetic(
        "dataframe/ArtificialData/data_mar_baseline_10000.csv",
        "dataframe/ArtificialData_complete/complete_data_mar_baseline_10000.csv",
        "MAR_10000"
    )
    final_results["MAR_10000"] = mar_res
    
    # 4. Collider Trap (Adversarial MAR) 10000
    collider_res = evaluate_collider_trap(
        "dataframe/ArtificialData/data_collider_trap_10000.csv",
        "dataframe/ArtificialData_complete/complete_data_collider_trap_10000.csv",
        "Collider_Trap_Adversarial_MAR_10000"
    )
    final_results["Collider_Trap_Adversarial_MAR_10000"] = collider_res
    
    metrics = ""
    for dataset, res in final_results.items():
        metrics += f"## {dataset}\n"
        if "Pima" in dataset:
            metrics += "| Model | Downstream F1 | Downstream AUROC |\n"
            metrics += "|-------|---------------|------------------|\n"
            for model, metrics in res.items():
                metrics += f"| {model} | {metrics['F1']:.4f} | {metrics['AUROC']:.4f} |\n"
        else:
            metrics += "| Model | MAE | RMSE | ATE Bias |\n"
            metrics += "|-------|-----|------|----------|\n"
            for model, metrics in res.items():
                metrics += f"| {model} | {metrics['MAE']:.4f} | {metrics['RMSE']:.4f} | {metrics['ATE_Bias']:.4f} |\n"
        metrics += "\n"
        
    print(metrics)

if __name__ == "__main__":
    main()
