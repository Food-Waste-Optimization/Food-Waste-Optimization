"""Creates ModelService class that allows requests to AI models."""

from __future__ import annotations

from itertools import zip_longest
from pathlib import Path

import polars as pl
from loguru import logger
from pandas import DataFrame

from src import config

from . import db
from .forecaster import (
    PerMealPOSForecaster,
    PerMealPOSForecasterGeneral,
    WholeRestaurantPOSForecaster,
    WholeRestaurantWasteForecaster,
)

DEFAULT_CO2 = 0.4
DEFAULT_WASTE = 0.01


def _hamming_distance(s1: str, s2: str) -> float:
    min_len = min(len(s1), len(s2))
    dist = sum(c1 != c2 for c1, c2 in zip_longest(s1, s2)) * 1.0 / min_len

    return dist


class ModelService:
    """Class for handling the connection between models, data and the app."""

    PATH_ROOT_TRAINED_MODEL = Path(config.TRAINED_MODELS)

    def __init__(
        self,
        name_whole_res_waste: str = "whole_restaurant_waste",
        name_whole_res_pos: str = "whole_restaurant_pos",
        name_per_meal_pos: str = "per_meal_pos",
    ) -> None:
        self.models = {}

        self.name_whole_res_waste = name_whole_res_waste
        self.name_whole_res_pos = name_whole_res_pos
        self.name_per_meal_pos = name_per_meal_pos

        self._load_models()

    def _load_models(self):
        # =================================================
        # Load Per meal POS forecasters
        # =================================================
        path_dir = ModelService.PATH_ROOT_TRAINED_MODEL / self.name_per_meal_pos / config.MODEL_TAG
        assert path_dir.exists()

        self.models[self.name_per_meal_pos] = {}

        # Load models of meals having historical data
        for path in path_dir.glob("*"):
            if not path.is_dir():
                continue

            self.models[self.name_per_meal_pos][path.stem] = PerMealPOSForecaster.load(path)

        # Load general model
        self.models[self.name_per_meal_pos]["general"] = PerMealPOSForecasterGeneral.load(path_dir)

        # =================================================
        # Load Whole restaurant POS forcaster
        # =================================================
        path_dir = ModelService.PATH_ROOT_TRAINED_MODEL / self.name_whole_res_pos / config.MODEL_TAG
        assert path_dir.exists()

        self.models[self.name_whole_res_pos] = {}
        for path in path_dir.glob("*"):
            self.models[self.name_whole_res_pos][path.stem] = WholeRestaurantPOSForecaster.load(path)

        # =================================================
        # Load Whole restaurant waste forcaster
        # =================================================
        path_dir = ModelService.PATH_ROOT_TRAINED_MODEL / self.name_whole_res_waste / config.MODEL_TAG
        assert path_dir.exists()

        self.models[self.name_whole_res_waste] = {}
        for path in path_dir.glob("*"):
            self.models[self.name_whole_res_waste][path.stem] = WholeRestaurantWasteForecaster.load(path)

    def _post_process(self, prediction):
        if prediction <= 0:
            prediction = 0.0

        prediction = round(prediction, 2)

        return prediction

    def forecast_waste_restaurant(self, restaurant: int, date: str) -> DataFrame | None:
        """Forecast waste for whole restaurant

        Args:
            restaurant (int): restaurant id
            date (str): date to forecast. Come under format '2025-01-01'

        Returns:
            DataFrame|None: forecasted waste in kg or None if error
        """
        if str(restaurant) not in self.models[self.name_whole_res_waste]:
            logger.error(f"Forecast whole restaurant waste: restaurant not found: {restaurant}")

            return None

        return self.models[self.name_whole_res_waste][str(restaurant)].forecast(date=date)

    def forecast_pos_per_meal(self, restaurant: int, meal_id: int, date: str, meal_type: int | None = None) -> float:
        model_name = f"{restaurant}_{meal_id}"

        if model_name not in self.models[self.name_per_meal_pos]:
            assert meal_type is not None
            out = self.models[self.name_per_meal_pos]["general"].forecast(
                date=date, restaurant=restaurant, meal_type=meal_type
            )
        else:
            out = self.models[self.name_per_meal_pos][model_name].forecast(
                date=date, restaurant=restaurant, meal_id=meal_id
            )

        pos = out["forecasted"].item()

        return pos

    def forecast_pos_restaurant(self, restaurant: int, date: str) -> DataFrame | None:
        if str(restaurant) not in self.models[self.name_whole_res_pos]:
            logger.error(f"Forecast whole restaurant pos: restaurant not found: {restaurant}")

            return None

        return self.models[self.name_whole_res_pos][str(restaurant)].forecast(date=date)

    def get_meals_prediction(self, restaurant: int, meals_data: dict) -> list[dict]:
        """Predict POS, waste and CO2 amount for meals given the menu

        Returns:
            list[dict]: List of records. Each record is a meal in restaurant with its predictions.
        """

        # =================================================
        # Find meal_id given the names in 'meals_data'
        # =================================================

        # Process meals_data to suitable format
        date = meals_data["date"]
        meals = pl.DataFrame(
            {
                "name": meals_data["meals"],
                "restaurant": [meals_data["restaurant"]] * len(meals_data["meals"]),
            }
        )

        # Get corresponding meal ids
        out = db.fetch_meal_info()
        dim_meals = pl.from_pandas(out)

        names_meal = dim_meals.select("meal_id", "name").explode("name")

        meal_ids = (
            meals
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


            # Get meal_type
            .join(dim_meals.select("meal_id", "meal_type"), on="meal_id", how="left")

            ["meal_id"]
            .to_list()
        )  # fmt: skip

        # logger.debug(f"meal_ids = {meal_ids}")

        # =================================================
        # Predict per-meal POS, waste and CO2
        # =================================================

        # Forecast whole-restaurant waste
        df = model.forecast_waste_restaurant(restaurant, date)
        assert df is not None
        waste_whole_res = df["forecasted"]

        # Forecast per-meal POS
        meals = db.fetch_meal_info_with_ids(meal_ids=meal_ids)
        meals["pcs"] = meals.apply(
            lambda r: model.forecast_pos_per_meal(restaurant, r["id"], date, r["meal_type"]),
            axis=1,
        )

        # Post-process
        meals["waste"] = waste_whole_res / meals["pcs"].sum()
        meals["name"] = meals_data["meals"]
        meals.drop(columns=["restaurants", "attributes", "meal_type", "names"], inplace=True)
        meals.rename(columns={"id": "meal_id", "meal_type_str": "meal_type"}, inplace=True)

        # logger.debug(f"hrerere: meals = {meals}")

        return meals.to_dict(orient="records")


model = ModelService()
