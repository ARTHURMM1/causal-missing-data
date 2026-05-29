# imputers/causal_imputer.py

from typing import Dict, List, Union

import numpy as np
import pandas as pd

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge
from sklearn.linear_model import LogisticRegression

from imputers.baseline import BaseImputer


class CausalImputer(BaseImputer):
    """
    Structurally Guided Causal Imputer

    Main ideas:
    -------------------------
    1. Missingness propensity:
        Estimate P(RW=1 | parents(RW))

    2. Graph-aware imputation:
        Restrict each imputation model
        to the Markov blanket of W

    3. Multiple imputation:
        Generate M imputed datasets

    4. Doubly robust weights:
        Inverse probability weighting
        using missingness propensity
    """

    def __init__(
        self,
        graph: Dict[str, List[str]],
        m: int = 20,
        random_state: int = 42,
    ):

        self.graph = graph
        self.m = m
        self.random_state = random_state

        self.propensity_models = {}
        self.dr_weights = None

    # ============================================================
    # Utility
    # ============================================================

    def _get_markov_blanket(
        self,
        node: str
    ) -> List[str]:
        """
        Simplified Markov blanket.

        Includes:
            - parents
            - children
            - parents of children
        """

        parents = set(
            self.graph.get(node, [])
        )

        children = set()

        for k, v in self.graph.items():
            if node in v:
                children.add(k)

        parents_of_children = set()

        for child in children:
            parents_of_children.update(
                self.graph.get(child, [])
            )

        mb = (
            parents
            | children
            | parents_of_children
        )

        mb.discard(node)

        return list(mb)

    # ============================================================
    # STEP 1
    # Missingness Propensity
    # ============================================================

    def _fit_missingness_models(
        self,
        df: pd.DataFrame
    ):

        rw_cols = [
            c for c in df.columns
            if c.startswith("RW")
        ]

        for rw in rw_cols:

            # Example:
            # RW1 -> W1
            w = rw.replace("RW", "W")

            # Parents of RW from graph
            features = self.graph.get(rw, [])

            if len(features) == 0:
                continue

            X = df[features]
            y = df[rw]

            model = LogisticRegression(
                max_iter=1000,
                random_state=self.random_state
            )

            model.fit(X, y)

            self.propensity_models[rw] = {
                "model": model,
                "features": features
            }

    # ============================================================
    # Fit
    # ============================================================

    def fit(
        self,
        X: Union[np.ndarray, pd.DataFrame]
    ) -> "CausalImputer":

        df = (
            pd.DataFrame(X)
            if isinstance(X, np.ndarray)
            else X.copy()
        )

        self._fit_missingness_models(df)

        return self

    # ============================================================
    # STEP 2
    # Graph-Aware Multiple Imputation
    # ============================================================

    def transform(
        self,
        X: Union[np.ndarray, pd.DataFrame]
    ) -> List[pd.DataFrame]:

        df = (
            pd.DataFrame(X)
            if isinstance(X, np.ndarray)
            else X.copy()
        )

        imputed_datasets = []

        for m_idx in range(self.m):

            current_df = df.copy()

            original_missing_masks = {
                col: current_df[col].isna()
                for col in current_df.columns
            }

            # =====================================================
            # Initial simple imputation
            # =====================================================

            for col in current_df.columns:

                if current_df[col].isna().sum() > 0:

                    mean_value = current_df[col].mean()

                    current_df[col] = current_df[col].fillna(
                        mean_value
                    )

            rng = np.random.default_rng(
                self.random_state + m_idx
            )
                
            w_cols = [
                c for c in df.columns
                if c.startswith("W")
            ]

            for iteration in range(5):
                for w in w_cols:

                    # missing_mask = (
                    #     current_df[w].isna()
                    # )
                    missing_mask = original_missing_masks[w]

                    if missing_mask.sum() == 0:
                        continue

                    # ----------------------------------------------
                    # Markov blanket restriction
                    # ----------------------------------------------

                    mb = self._get_markov_blanket(w)

                    features = [
                        f for f in mb
                        if f in current_df.columns
                    ]

                    # remove missingness indicators
                    features = [
                        f for f in features
                        if not f.startswith("RW")
                    ]

                    observed_mask = (
                        current_df[w].notna()
                    )

                    train_df = current_df.loc[
                        observed_mask
                    ]

                    X_train = train_df[features]
                    y_train = train_df[w]

                    # ----------------------------------------------
                    # Structural regression model
                    # ----------------------------------------------

                    model = BayesianRidge()

                    model.fit(
                        X_train,
                        y_train
                    )

                    X_missing = current_df.loc[
                        missing_mask,
                        features
                    ]

                    pred_mean, pred_std = model.predict(
                        X_missing,
                        return_std=True
                    )

                    # ----------------------------------------------
                    # Multiple imputation sampling
                    # ----------------------------------------------

                    sampled_values = rng.normal(
                        loc=pred_mean,
                        scale=pred_std
                    )

                    current_df.loc[
                        missing_mask,
                        w
                    ] = sampled_values

                    # print(
                    #     "iteration",
                    #     iteration,
                    #     "variable",
                    #     w,
                    #     "missing",
                    #     missing_mask.sum()
                    # )
                    
            imputed_datasets.append(
                current_df
            )

        return imputed_datasets

    # ============================================================
    # STEP 3
    # Doubly Robust Weights
    # ============================================================

    def get_dr_weights(
        self,
        X: Union[np.ndarray, pd.DataFrame]
    ) -> pd.DataFrame:

        df = (
            pd.DataFrame(X)
            if isinstance(X, np.ndarray)
            else X.copy()
        )

        rw_cols = [
            c for c in df.columns
            if c.startswith("RW")
        ]

        weights = pd.DataFrame(
            index=df.index
        )

        for rw in rw_cols:

            if rw not in self.propensity_models:
                continue

            info = self.propensity_models[rw]

            model = info["model"]
            features = info["features"]

            probs = model.predict_proba(
                df[features]
            )[:, 1]

            probs = np.clip(
                probs,
                1e-3,
                1 - 1e-3
            )

            weights[rw] = 1.0 / probs

        self.dr_weights = weights

        return weights

    # ============================================================
    # Rubin-style pooling
    # ============================================================

    def pooled_ate(
        self,
        datasets: List[pd.DataFrame]
    ) -> float:

        ates = []

        for df in datasets:

            treated = (
                df[df["X"] == 1]["Y"]
                .mean()
            )

            control = (
                df[df["X"] == 0]["Y"]
                .mean()
            )

            ate = treated - control

            ates.append(ate)

        return float(np.mean(ates))