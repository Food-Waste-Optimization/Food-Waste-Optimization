from __future__ import annotations

import logging
import sys
import warnings
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd
from darts.models import CatBoostModel, NaiveMovingAverage
from darts.models.forecasting.forecasting_model import ForecastingModel
from loguru import logger
from pandas import DataFrame, Timestamp

warnings.filterwarnings("ignore")

logging.getLogger("lightning").setLevel(0)


class Forecaster(ABC):
    @classmethod
    @abstractmethod
    def load(cls, path_dir: Path, **kwargs) -> Forecaster:
        pass

    @abstractmethod
    def forecast(self, date: str, **kwargs) -> DataFrame:
        """Forecast

        Args:
            date (str): date to forecast

        Returns:
            DataFrame: Dataframe having 2 columns: 'date' and 'forecasted'
        """

        pass


class WholeRestaurantWasteForecaster(Forecaster):
    def __init__(self, model: ForecastingModel) -> None:
        super().__init__()

        self.model = model

        assert self.model.training_series, "Loaded model not contained training_series"

    @classmethod
    def load(cls, path_dir: Path, **kwargs) -> WholeRestaurantWasteForecaster:
        path_model = path_dir / "model.pt"
        model = CatBoostModel.load(path_model.as_posix())

        return WholeRestaurantWasteForecaster(model)

    def forecast(self, date: str, **kwargs) -> DataFrame:
        assert self.model.training_series
        last_training_date = self.model.training_series.time_index[-1]
        assert isinstance(last_training_date, Timestamp)

        days = len(pd.date_range("2025-03-31", "2025-06-06", freq="b"))
        if days <= 0:
            logger.error(f"Forecasting date ({date}) must be after {last_training_date.date().strftime(r'%Y-%m-%d')}")
            sys.exit(1)

        preds_ts = self.model.predict(days, verbose=False)

        out = pd.DataFrame({"date": preds_ts.time_index, "forecasted": preds_ts.values().squeeze()})

        return out


class WholeRestaurantPOSForecaster(Forecaster):
    def __init__(
        self,
        model: ForecastingModel,
    ) -> None:
        super().__init__()

        self.model = model

        assert self.model.training_series, "Loaded model not contained training_series"

    @classmethod
    def load(cls, path_dir: Path, **kwargs) -> WholeRestaurantPOSForecaster:
        path_model = path_dir / "model.pt"
        model = CatBoostModel.load(path_model)

        return WholeRestaurantPOSForecaster(model)

    def forecast(self, date: str, **kwargs) -> DataFrame:
        assert self.model.training_series
        last_training_date = self.model.training_series.time_index[-1]
        assert isinstance(last_training_date, Timestamp)

        days = len(pd.date_range(last_training_date, date, freq="b"))
        if days <= 0:
            logger.error(f"Forecasting date ({date}) must be after {last_training_date.date().strftime(r'%Y-%m-%d')}")
            sys.exit(1)

        preds_ts = self.model.predict(days, verbose=False)

        out = pd.DataFrame({"date": preds_ts.time_index, "forecasted": preds_ts.values().squeeze()})

        return out


class PerMealPOSForecasterGeneral(Forecaster):
    """Forecaster applied for new meals (meals having no historical data)"""

    def __init__(self, historical_pos: DataFrame) -> None:
        super().__init__()

        self.historical_pos = historical_pos

    @classmethod
    def load(cls, path_dir: Path, **kwargs) -> Forecaster:
        filename = kwargs.get("filename", "general_pos.csv")
        path_file: Path = path_dir / filename

        if not path_file.exists():
            logger.error(f"Load PerMealPOSForecasterGeneral: File not found: {path_file.as_posix()}")
            sys.exit(1)

        historical_pos = pd.read_csv(path_file)
        return PerMealPOSForecasterGeneral(historical_pos)

    def forecast(self, date: str, **kwargs) -> DataFrame:
        restaurant, meal_type = kwargs.get("restaurant"), kwargs.get("meal_type")

        pred = self.historical_pos[
            (self.historical_pos["restaurant"] == restaurant) & (self.historical_pos["meal_type"] == meal_type)
        ]["pcs"].item()

        return DataFrame({"date": [date], "forecasted": [pred]})


class PerMealPOSForecaster(Forecaster):
    """Forecaster dedicated for meals having historical data (i.e. having model)"""

    def __init__(self, model: "ForecastingModel") -> None:
        self.model = model

    @classmethod
    def load(cls, path_dir: Path, **kwargs) -> PerMealPOSForecaster:
        # Load saved model
        path_model = path_dir / "model.pt"

        model = NaiveMovingAverage.load(path_model)

        return PerMealPOSForecaster(model)

    def forecast(self, date: str, **kwargs) -> DataFrame:
        # Forecast
        pred = self.model.predict(1, verbose=False).to_series().values.squeeze()

        return DataFrame({"date": [date], "forecasted": [pred]})


# =================================================
# Model service
# =================================================

TAG = "May_26"


class ModelService:
    PATH_ROOT_TRAINED_MODEL = Path("trained_models")

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
        path_dir = ModelService.PATH_ROOT_TRAINED_MODEL / self.name_per_meal_pos / TAG
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
        path_dir = ModelService.PATH_ROOT_TRAINED_MODEL / self.name_whole_res_pos / TAG
        assert path_dir.exists()

        self.models[self.name_whole_res_pos] = {}
        for path in path_dir.glob("*"):
            self.models[self.name_whole_res_pos][path.stem] = WholeRestaurantPOSForecaster.load(path)

        # =================================================
        # Load Whole restaurant waste forcaster
        # =================================================
        path_dir = ModelService.PATH_ROOT_TRAINED_MODEL / self.name_whole_res_waste / TAG
        assert path_dir.exists()

        self.models[self.name_whole_res_waste] = {}
        for path in path_dir.glob("*"):
            self.models[self.name_whole_res_waste][path.stem] = WholeRestaurantWasteForecaster.load(path)

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

    def forecast_pos_restaurant(self, restaurant: int, date: str) -> float | None:
        if str(restaurant) not in self.models[self.name_whole_res_pos]:
            logger.error(f"Forecast whole restaurant pos: restaurant not found: {restaurant}")

            return None

        return self.models[self.name_whole_res_pos][str(restaurant)].forecast(date=date)


def main():
    try:
        # print(ModelService().forecast_waste_restaurant(1, "2025-05-02"))
        # print(ModelService().forecast_pos_restaurant(1, "2025-05-02"))
        # print(ModelService().forecast_pos_per_meal(1, 1243, "2025-05-02", 2))
        print(ModelService().forecast_pos_per_meal(1, 51, "2025-06-05", 1))
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    sys.exit(main())
