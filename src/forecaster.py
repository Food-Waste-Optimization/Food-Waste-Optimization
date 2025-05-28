from __future__ import annotations

import logging
import sys
import warnings
from abc import ABC, abstractmethod
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import polars as pl
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from darts.models import CatBoostModel, LinearRegressionModel, NaiveMovingAverage
from darts.models.forecasting.forecasting_model import ForecastingModel
from darts.utils.utils import generate_index
from loguru import logger
from pandas import DataFrame

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
        last_training_date = self.model.training_series.time_index[-1]
        days = (pd.to_datetime(date) - last_training_date).days
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
        days = (pd.to_datetime(date) - last_training_date).days
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

    def __init__(self, model: "ForecastingModel", transformer_tgt: Scaler, transformer_cov: Scaler | None) -> None:
        self.model = model
        self.transformer_tgt = transformer_tgt
        self.transformer_cov = transformer_cov

    @classmethod
    def load(cls, path_dir: Path, **kwargs) -> PerMealPOSForecaster:
        # Load saved model
        path_model = path_dir / "model.pt"
        path_scaler_tgt = path_dir / "scaler_tgt.gz"

        model = LinearRegressionModel.load(path_model)
        transformer_tgt = joblib.load(path_scaler_tgt)

        # Load covariate transformer
        if isinstance(model, LinearRegressionModel):
            path_scaler_cov = path_dir / "scaler_cov.gz"
            transformer_cov = joblib.load(path_scaler_cov)
        else:
            transformer_cov = None

        return PerMealPOSForecaster(model, transformer_tgt, transformer_cov)

    def forecast(self, date: str, **kwargs) -> DataFrame:
        # Forecast
        match self.model:
            case NaiveMovingAverage():
                preds_raw = self.model.predict(1, verbose=False)
            case LinearRegressionModel():
                # Prepare date covariate
                cov_df = (
                    pl
                    .DataFrame()
                    .with_columns(
                        pl.lit(date).str.to_date().alias('date')
                    )
                    .with_columns(
                        pl.col('date').dt.weekday().alias('weekday'),
                        pl.col('date').dt.day().alias('day'),
                        pl.col('date').dt.week().alias('week'),
                        pl.col('date').dt.month().alias('month'),
                        pl.col('date').dt.year().alias('year'),
                    )
                    .with_columns(
                        (pl.col('weekday') * 2 * np.pi / 7).sin().alias('weekday_sin'),
                        (pl.col('weekday') * 2 * np.pi / 7).cos().alias('weekday_cos'),
                        (pl.col('day') * 2 * np.pi / 31).sin().alias('day_sin'),
                        (pl.col('day') * 2 * np.pi / 31).cos().alias('day_cos'),
                        (pl.col('week') * 2 * np.pi / 53).sin().alias('week_sin'),
                        (pl.col('week') * 2 * np.pi / 53).cos().alias('week_cos'),
                        (pl.col('month') * 2 * np.pi / 12).sin().alias('month_sin'),
                        (pl.col('month') * 2 * np.pi / 12).cos().alias('month_cos'),
                    )
                    .drop('date')
                    .to_pandas()
                )  # fmt: skip
                idx_cov = len(self.model.future_covariate_series.time_index)
                series_cov_new = TimeSeries.from_times_and_values(
                    times=generate_index(idx_cov, idx_cov), values=cov_df.to_numpy(), columns=cov_df.columns
                )

                series_cov_new_transformed = self.transformer_cov.transform(series_cov_new)

                # Predict
                preds_raw = self.model.predict(1, future_covariates=series_cov_new_transformed)
            case _:
                raise NotImplementedError()

        # Post-process forecasted
        pred = self.transformer_tgt.inverse_transform(preds_raw).to_series().item()

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

    def forecast_pos_per_meal(
        self, restaurant: int, meal_id: int, date: str, meal_type: int | None = None
    ) -> float | None:
        model_name = f"{restaurant}_{meal_id}"

        if model_name not in self.models[self.name_per_meal_pos]:
            out = self.models[self.name_per_meal_pos]["general"].forecast(
                date=date, restaurant=restaurant, meal_type=meal_type
            )
        else:
            out = self.models[self.name_per_meal_pos][model_name].forecast(
                date=date, restaurant=restaurant, meal_id=meal_id
            )

        return out

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
        print(ModelService().forecast_pos_per_meal(1, 10, "2025-05-02"))
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    sys.exit(main())
