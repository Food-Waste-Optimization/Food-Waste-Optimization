"""Creates ModelService class that allows requests to AI models."""

import os
from itertools import permutations
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

# from darts.models import ARIMA, LightGBMModel, LinearRegressionModel
from loguru import logger
from pandas import DataFrame
from xgboost import XGBRegressor

from . import db

cols_X = [
    "weekday_sin",
    "weekday_cos",
    "day_sin",
    "day_cos",
    "month_sin",
    "month_cos",
    "restaurant",
    "meal_id_enc",
    "meal_type",
    "pcs_mean",
    "meal_id_other1_enc",
    "meal_id_other2_enc",
    "meal_id_other3_enc",
    "meal_id_other4_enc",
    "meal_type_other1",
    "meal_type_other2",
    "meal_type_other3",
    "meal_type_other4",
    "pcs_mean_other1",
    "pcs_mean_other2",
    "pcs_mean_other3",
    "pcs_mean_other4",
]

cols = [
    "index",
    "date",
    "restaurant",
    "meal_id",
    "meal_type",
    "pcs_mean",
    "idx_tup",
    "meal_id_other1_enc",
    "meal_id_other2_enc",
    "meal_id_other3_enc",
    "meal_id_other4_enc",
    "meal_type_other1",
    "meal_type_other2",
    "meal_type_other3",
    "meal_type_other4",
    "pcs_mean_other1",
    "pcs_mean_other2",
    "pcs_mean_other3",
    "pcs_mean_other4",
]

cols_cat = [
    "restaurant",
    "meal_type",
    "meal_type_other1",
    "meal_type_other2",
    "meal_type_other3",
    "meal_type_other4",
]
map_mealtype = {
    "meat": 1,  # 'meat',
    "fish": 2,  # 'fish',
    "vegan": 3,  # 'vegan',
    "vegetarian": 4,  # 'vegetarian',
    "chicken": 5,  # 'chicken'
}

map_restaurantcode2str = {
    "che": "Chemicum",
    "exa": "Exactum",
    "phy": "Physicum",
    "vik": "Vikki",
}


class ModelService:
    """Class for handling the connection between models, data and the app."""

    PATH_ROOT_TRAINED_MODEL = Path(os.getenv("TRAINED_MODELS", "/trained_models"))

    def __init__(self):
        # data is fetched every time init is run, this should not happen\
        self.models = {
            "receipt": {},
            "biowaste": {},
            "occupancy": {},
            "meal": {},
            "receipt_per_day": None,
            "biowaste_from_meal": {},
            "co2_from_meal": {},
            "per_day_POS": None,
            "encoder": None,
        }
        # self._load_receipt_forecaster()
        # self._load_biowaste_forecaster()
        # self._load_occupancy_forecaster()
        # self._load_meal_forecaster()

        # self._load_receipt_byday_forecaster()
        # self._load_biowaste_from_meal_forecaster()
        # self._load_co2_from_meal_forecaster()

        self._load_model_phase4()

        # self.data = data_repo.get_model_fit_data()
        # self.model = NeuralNetwork(
        #     data=self.data)

    def _load_model_phase4(self):
        logger.info("Load trained model for per-meal POS forecast and encoder")

        path = ModelService.PATH_ROOT_TRAINED_MODEL / "pos/phase_4/xgb_cat_Nov13.json"
        self.models["per_day_POS"] = XGBRegressor(
            tree_method="hist", enable_categorical=True
        )
        self.models["per_day_POS"].load_model(path)

        path = (
            ModelService.PATH_ROOT_TRAINED_MODEL
            / "encoder/phase_4/targetenc_meal_id_Nov13.pkl"
        )
        self.models["encoder"] = joblib.load(path)

    def _post_process(self, prediction):
        if prediction <= 0:
            prediction = 0.0

        prediction = round(prediction, 2)

        return prediction

    def forecast_pos(self, meals: DataFrame) -> DataFrame | None:
        """Predict the POS for each meal in a specific date given the list of meal ids

        Args:
            meals (DataFrame): input dataframe

        Returns:
            DataFrame|None: predicted POS
        """

        # Read from database the info of given meal_ids
        dim_meals = db.fetch_meal_info_with_ids(meal_ids=meals["meal_id"].tolist())

        if len(dim_meals) == 0:
            return None

        feat = (
            meals.merge(dim_meals, left_on="meal_id", right_on="id", how="left")
            .copy()
            .drop(columns="id")
        )

        # Create columns for other and encode them
        meal_ids = (
            meals.groupby(["index", "date", "restaurant"])["meal_id"]
            .apply(lambda x: list(x))
            .reset_index()
            .rename(columns={"meal_id": "meal_ids"})
        )
        feat = feat.merge(meal_ids, on=["index", "date", "restaurant"], how="left")

        # Create columns for other and encode them
        THETA = 5
        records = []
        for r in feat.itertuples():
            ids = set(r.meal_ids)
            ids.remove(r.meal_id)

            for idx_tup, tup in enumerate(permutations(ids)):
                tup = [*tup]

                # pad
                if len(tup) < THETA - 1:
                    tup.extend([0] * (THETA - 1 - len(tup)))

                for idx, m_id in enumerate(tup):
                    records.append(
                        {
                            "index": r.index,
                            "date": r.date,
                            "restaurant": r.restaurant,
                            "meal_id": r.meal_id,
                            "meal_type": r.type,
                            "pcs_mean": r.mean,
                            "idx_tup": idx_tup,
                            "other": idx + 1,
                            "meal_id_other": m_id,
                        }
                    )

        feat = (
            pd.DataFrame.from_records(records)
            .merge(dim_meals, how="left", left_on="meal_id_other", right_on="id")
            .drop(columns="id")
            .rename(columns={"type": "meal_type_other", "mean": "pcs_mean_other"})
        )

        encoded = self.models["encoder"].transform(
            feat["meal_id_other"].to_numpy().reshape(-1, 1)
        )
        mask = (feat["meal_id_other"] != 0).astype(np.int32)
        feat["meal_id_other_enc"] = encoded.squeeze() * mask

        feat["meal_type_other"] = feat["meal_type_other"].map(map_mealtype)

        feat = feat.fillna(0)

        cols_idx = [
            "index",
            "date",
            "restaurant",
            "meal_id",
            "meal_type",
            "pcs_mean",
            "idx_tup",
        ]
        feat = feat.pivot(
            index=cols_idx,
            columns="other",
            values=["pcs_mean_other", "meal_type_other", "meal_id_other_enc"],
        ).reset_index()

        feat.columns = cols

        feat.drop(columns="idx_tup", inplace=True)

        # Encode main columns
        feat["meal_type"] = feat["meal_type"].map(map_mealtype)

        def _encode_date_cyclic(
            t, period_week: int = 7, period_day: int = 31, period_month: int = 12
        ):
            def get_sin_encoding(x, period: int):
                return np.sin(2 * np.pi * x / period)

            def get_cos_encoding(x, period: int):
                return np.cos(2 * np.pi * x / period)

            return pd.Series(
                {
                    "weekday_sin": get_sin_encoding(t.weekday(), period_week),
                    "weekday_cos": get_cos_encoding(t.weekday(), period_week),
                    "day_sin": get_sin_encoding(t.day, period_day),
                    "day_cos": get_cos_encoding(t.day, period_day),
                    "month_sin": get_sin_encoding(t.month, period_month),
                    "month_cos": get_cos_encoding(t.month, period_month),
                }
            )

        datetime_encoded = feat["date"].apply(_encode_date_cyclic)
        feat = pd.concat([feat, datetime_encoded], axis=1)

        feat["meal_id_enc"] = self.models["encoder"].transform(
            feat["meal_id"].to_numpy().reshape(-1, 1)
        )

        feat["restaurant_raw"] = feat["restaurant"].copy()
        feat["restaurant"] = feat["restaurant"].map(
            {
                "che": 1,  #'chemicum',
                "phy": 2,  #'physicum',
                "exa": 3,  #'exactum'
            }
        )

        # Assign categorical column type
        for col in cols_cat:
            feat[col] = feat[col].astype("category")

        # Keep important columns
        X = feat[cols_X]

        feat["pcs_pred"] = np.clip(
            self.models["per_day_POS"].predict(X),
            a_min=0,
            a_max=None,
        )

        pred = (
            feat.groupby(["index", "date", "restaurant_raw", "meal_id"], observed=True)[
                "pcs_pred"
            ]
            .mean()
            .reset_index()
            .rename(columns={"restaurant_raw": "restaurant"})
        )

        # Post process
        pred.rename(columns={"pcs_pred": "pcs"}, inplace=True)
        pred["pcs"] = pred["pcs"].clip(0).astype(int)
        output = pred[["meal_id", "pcs"]]

        return output
