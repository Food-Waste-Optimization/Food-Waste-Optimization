from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd
from darts.models import CatBoostModel, NaiveMovingAverage
from darts.models.forecasting.forecasting_model import ForecastingModel
from loguru import logger
from pandas import DataFrame, Timestamp


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

        days = len(pd.date_range(last_training_date, date, freq="b"))
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
        pred = self.model.predict(1, verbose=False).to_series().values.squeeze().item()

        return DataFrame({"date": [date], "forecasted": [pred]})
