"""Creates ModelService class that allows requests to AI models."""

import os
from datetime import datetime
from itertools import zip_longest
from pathlib import Path

import lightgbm
import numpy as np
import pandas as pd
import polars as pl
import requests

# from darts.models import ARIMA, LightGBMModel, LinearRegressionModel
from loguru import logger

from . import db

URL_YLVA_API = "https://unicafe.fi/wp-json/swiss/v1/restaurants?wpml_language=en"
RESTAURANTS = ["Viikuna", "Physicum", "Exactum", "Chemicum"]
ENTRY_TYPES = {
    "Tiedoitus": "Notification",
    "Lisuke": "Side dish",
    "Makeasti": "Sweet",
}

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

map_weekday2abbr = {
    0: "Ma",
    1: "Ti",
    2: "Ke",
    3: "To",
    4: "Pe",
}
map_restaurant = {
    "Physicum": "phy",
    "Chemicum": "che",
    "Exactum": "exa",
    "Viikuna": "vik",
}
indices = pl.from_records(
    [
        {"restaurant": "phy", "index": 1},
        {"restaurant": "che", "index": 2},
        {"restaurant": "exa", "index": 3},
        {"restaurant": "vik", "index": 4},
    ]
)


def _get_today() -> str:
    today = datetime.now()

    assert today.weekday() <= 4
    weekday = map_weekday2abbr[datetime.now().weekday()]

    return f"{weekday} {today.strftime('%d.%m.')}"


def _hamming_distance(s1: str, s2: str) -> float:
    min_len = min(len(s1), len(s2))
    dist = sum(c1 != c2 for c1, c2 in zip_longest(s1, s2)) * 1.0 / min_len

    return dist


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

        path = Path(os.getenv("MODEL_POS_FORECASTING", ""))
        logger.debug(
            f"path per-meal POS forecasting: {os.getenv('MODEL_POS_FORECASTING')}"
        )
        self.models["per_day_POS"] = lightgbm.Booster(model_file=path)

        path = Path(os.getenv("DIM_MEAL_EMBDS", ""))
        self.meal_embds = pl.read_parquet(path)

        path = Path(os.getenv("DIM_TOPK", ""))
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

    def get_today_meals_prediction(self) -> list[dict]:
        """Predict POS, waste and CO2 amount for meals in today' menu across restaurants

        Returns:
            list[dict]: List of records. Each record is a meal in restaurant with its predictions.
        """

        # Parse meal names in raw string YLVA API
        response = requests.get(URL_YLVA_API).json()

        today = _get_today()
        restaurants_list = []
        for record in response:
            if record["title"] in RESTAURANTS:
                for menu in record["menuData"]["menus"]:
                    if menu["date"] == today:
                        meals = []
                        for meal in menu["data"]:
                            # Check if being one of the ignored cases
                            if meal["price"]["name"] in ENTRY_TYPES:
                                logger.debug(
                                    f"{meal['name']} -> {ENTRY_TYPES[meal['price']['name']]}"
                                )
                                continue

                            meals.append(
                                {"name": meal["name"], "metadata": meal["meta"]["0"]}
                            )

                        meals_df = pl.from_records(meals).with_columns(
                            pl.lit(record["title"]).alias("restaurant")
                        )

                        restaurants_list.append(meals_df)
        restaurants = pl.concat(restaurants_list)

        # Get corresponding meal ids
        out = db.fetch_meal_info()
        dim_meals = pl.from_pandas(out)

        names_meal = dim_meals.select("meal_id", "name").explode("name")

        menus: pl.DataFrame = (
            restaurants
            # Find most probable meal in the database for each entry
            .join(names_meal, how="cross")
            .with_columns(
                pl.struct("name", "name_right")
                .map_elements(
                    lambda x: _hamming_distance(x["name"], x["name_right"]),
                    return_dtype=pl.Float32,
                )
                .alias("dist")
            )
            .group_by("name", "restaurant")
            .agg(pl.all().sort_by("dist").first())
            .drop("name_right", "dist")
            # Remap values in column `restaurant`
            .with_columns(pl.col("restaurant").replace(map_restaurant))
            # Get meal_type
            .join(dim_meals.select("meal_id", "meal_type"), on="meal_id", how="left")
            # Add column `date`
            .with_columns(pl.lit(datetime.now()).dt.date().alias("date"))
            # Add column `index` (indicate which meals come in same menu)
            .join(indices, on="restaurant", how="left")
        )

        # Predict POS, waste and CO2
        pos = self.forecast_pos(
            menus.select("index", "meal_id", "date", "restaurant").to_pandas()
        )
        assert pos is not None
        pos = pos[["meal_id", "restaurant", "pcs_pred"]].rename(
            columns={"pcs_pred": "pcs"}
        )

        meal_ids = pos["meal_id"].tolist()
        co2 = db.fetch_co2_with_ids(meal_ids=meal_ids)
        biowaste = db.fetch_waste_with_ids(meal_ids=meal_ids)

        menus = (
            menus.join(pl.from_pandas(pos), on=["meal_id", "restaurant"], how="left")
            .join(pl.from_pandas(co2), on="meal_id", how="left")
            .join(pl.from_pandas(biowaste), on="meal_id", how="left")
        )

        # Post-process
        menus = menus.with_columns(pl.col("date").dt.strftime("%Y-%m-%d"))

        return menus.to_dicts()
