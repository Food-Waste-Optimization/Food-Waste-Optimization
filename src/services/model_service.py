"""Creates ModelService class that allows requests to AI models."""

import os
from pathlib import Path

import lightgbm
import numpy as np
import pandas as pd
import polars as pl

# from darts.models import ARIMA, LightGBMModel, LinearRegressionModel
from loguru import logger

from . import db

dim_mealtype2id = pl.DataFrame(
    [
        {"meal_type": "meat", "meal_type_enc": 0},
        {"meal_type": "vegetarian", "meal_type_enc": 1},
        {"meal_type": "chicken", "meal_type_enc": 2},
        {"meal_type": "fish", "meal_type_enc": 3},
        {"meal_type": "vegan", "meal_type_enc": 3},
    ]
)
dim_restaurant2id = pl.DataFrame(
    [
        {"restaurant": "phy", "restaurant_enc": 0},
        {"restaurant": "che", "restaurant_enc": 1},
        {"restaurant": "exa", "restaurant_enc": 2},
        {"restaurant": "vik", "restaurant_enc": 3},
    ]
)


cols_X = [
    "meal_id_right",
    "pcs_mean",
    "dist",
    "meal_type_enc",
    "restaurant_enc",
    "serving_percent",
    "weekday_sin",
    "weekday_cos",
    "day_sin",
    "day_cos",
    "month_sin",
    "month_cos",
]
cols_cat = [
    "meal_id_right",
    "meal_type_enc",
    "restaurant_enc",
]


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

        path = ModelService.PATH_ROOT_TRAINED_MODEL / "pos/phase_4/lightbgm_Jan21.txt"
        self.models["per_day_POS"] = lightgbm.Booster(model_file=path)

        path = (
            ModelService.PATH_ROOT_TRAINED_MODEL
            / "encoder/phase_4/dim_meal_embds_Jan21.parquet"
        )
        self.meal_embds = pl.read_parquet(path)

        path = (
            ModelService.PATH_ROOT_TRAINED_MODEL
            / "encoder/phase_4/dim_topK_Jan21.parquet"
        )
        self.topK = pl.read_parquet(path)

    def _post_process(self, prediction):
        if prediction <= 0:
            prediction = 0.0

        prediction = round(prediction, 2)

        return prediction

    def forecast_pos(self, meals: pd.DataFrame) -> pd.DataFrame | None:
        """Predict the POS for each meal in a specific date given the list of meal ids

        Args:
            meals (DataFrame): input dataframe

        Returns:
            DataFrame|None: predicted POS
        """

        # Read from database the info of given meal_ids
        dim_meals = pl.from_dataframe(
            db.fetch_meal_info_with_ids(meal_ids=meals["meal_id"].tolist())
        )

        if len(dim_meals) == 0:
            return None

        meal_types = dim_meals.select(
            pl.col("id").alias("meal_id"), pl.col("type").alias("meal_type")
        )

        # logger.debug(meal_types)
        # logger.debug(pl.from_dataframe(meals))

        feat = (
            pl.from_dataframe(meals)
            .join(meal_types, on="meal_id", how="left")
            .join(self.topK, on=["restaurant", "meal_type"], how="left")
            .join(self.meal_embds, on=["meal_id", "meal_id_right"], how="left")
        )

        # Encode restaurant
        feat = feat.join(dim_restaurant2id, on="restaurant")

        # Encode meal_type
        feat = feat.join(dim_mealtype2id, on="meal_type")

        # Encode datetime
        feat = (
            feat.with_columns(
                pl.col("date").dt.weekday().alias("weekday"),
                pl.col("date").dt.day().alias("day"),
                pl.col("date").dt.month().alias("month"),
            )
            .with_columns(
                (pl.col("weekday") * 2 * np.pi / 7).sin().alias("weekday_sin"),
                (pl.col("weekday") * 2 * np.pi / 7).cos().alias("weekday_cos"),
                (pl.col("day") * 2 * np.pi / 31).sin().alias("day_sin"),
                (pl.col("day") * 2 * np.pi / 31).cos().alias("day_cos"),
                (pl.col("month") * 2 * np.pi / 12).sin().alias("month_sin"),
                (pl.col("month") * 2 * np.pi / 12).cos().alias("month_cos"),
            )
            .drop("weekday", "day", "month")
        )

        # Add `serving_percent`
        feat = feat.with_columns(pl.lit(1.0).alias("serving_percent"))

        # Prepare data for inference
        X = feat.select(cols_X).to_pandas()

        for col in cols_cat:
            X[col] = X[col].astype("category")

        # Predict
        pcs_pred = np.clip(self.models["per_day_POS"].predict(X), a_min=0, a_max=None)
        feat = feat.with_columns(pl.Series(pcs_pred).alias("pcs_pred"))

        output = (
            feat.group_by(["index", "date", "restaurant", "meal_id"])
            .agg(
                pl.col("pcs_pred").mean(),
            )
            .to_pandas()
        )

        return output
