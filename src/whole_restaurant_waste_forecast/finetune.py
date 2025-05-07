import argparse
import datetime
import sys
from functools import partial

import holidays
import numpy as np
import optuna
import pandas as pd
import polars as pl
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from darts.models import (
    CatBoostModel,
    LightGBMModel,
    NBEATSModel,
    RNNModel,
    TFTModel,
    TransformerModel,
    TSMixerModel,
    XGBModel,
)

# from lightning.pytorch.loggers import TensorBoardLogger
from loguru import logger
from optuna.trial import Trial
from pytorch_lightning.callbacks import TQDMProgressBar
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.preprocessing import MinMaxScaler

CUTOFF_DATE = pd.to_datetime("2025-01-01")
EPS = 1e-6


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--restaurant", "-r", type=str, choices=["che", "vik", "phy", "exa"], dest="restaurant")

    args = parser.parse_args()

    return args


def _f_objective(
    trial: Trial,
    restaurant: str,
    model_name: str,
    series_train_transformed: TimeSeries,
    series_test: TimeSeries,
    series_cov: TimeSeries,
    transformer_target: Scaler,
):
    # =================================================
    # Train
    # =================================================

    input_chunk_length = trial.suggest_categorical("input_chunk_length", [2, 3, 5, 7, 15, 30, 40, 60])
    output_chunk_length = trial.suggest_categorical("output_chunk_length", [1, 7, 15, 30, 60, len(series_test)])
    num_epochs = trial.suggest_categorical("num_epochs", [200, 400, 600])

    version = datetime.datetime.now().strftime("%m-%d_%H-%M-%S")

    # Define params
    add_encoders = {
        "datetime_attribute": {"future": ["dayofweek", "day", "month"], "past": ["dayofweek", "day", "month"]},
        "cyclic": {"past": ["dayofweek", "day", "month"], "future": ["dayofweek", "day", "month"]},
    }

    params_ml = {
        "lags": input_chunk_length,
        "lags_future_covariates": [0],
        "output_chunk_length": output_chunk_length,
        "add_encoders": {**add_encoders},
    }
    params_dl = {
        "input_chunk_length": input_chunk_length,
        "output_chunk_length": output_chunk_length,
        "add_encoders": {**add_encoders},
        "n_epochs": num_epochs,
        "pl_trainer_kwargs": {
            "callbacks": [TQDMProgressBar(refresh_rate=4)],
            "logger": [
                # TensorBoardLogger(
                #     "logs/tensorboard", name=f"{model_name}-{restaurant}", version=version, default_hp_metric=False
                # )
            ],
            "precision": "32-true",
        },
        "optimizer_kwargs": {"lr": 5e-4},
    }

    # Train
    try:
        match model_name:
            # =================================================
            # ML models
            # =================================================
            case "catboost":
                model = CatBoostModel(**params_ml)
                model.fit(series_train_transformed, future_covariates=series_cov)
            case "xgboost":
                model = XGBModel(**params_ml)
                model.fit(series_train_transformed, future_covariates=series_cov)
            case "lightbgm":
                model = LightGBMModel(**params_ml)
                model.fit(series_train_transformed, future_covariates=series_cov)

            # =================================================
            # DL models
            # =================================================
            case "rnn":
                params_dl["model"] = "LSTM"

                model = RNNModel(**params_dl)
                model.fit(series_train_transformed, future_covariates=series_cov)
            case "tsmixer":
                model = TSMixerModel(**params_dl)
                model.fit(series_train_transformed, future_covariates=series_cov)
            case "transformer":
                model = TransformerModel(**params_dl)
                model.fit(series_train_transformed, past_covariates=series_cov.split_before(CUTOFF_DATE)[0])
            case "tft":
                params_dl["categorical_embedding_sizes"] = {"holiday": (2, 2), "exam": (2, 2), "restaurant": (4, 4)}

                model = TFTModel(**params_dl)
                model.fit(series_train_transformed, future_covariates=series_cov)
            case "n-beats":
                model = NBEATSModel(**params_dl)
                model.fit(series_train_transformed, past_covariates=series_cov.split_before(CUTOFF_DATE)[0])

            case _:
                raise NotImplementedError()

        # =================================================
        # Test
        # =================================================
        match model_name:
            # =================================================
            # ML models
            # =================================================
            case "catboost":
                series_pred = model.predict(n=len(series_test), future_covariates=series_cov)
            case "xgboost":
                series_pred = model.predict(n=len(series_test), future_covariates=series_cov)
            case "lightbgm":
                series_pred = model.predict(n=len(series_test), future_covariates=series_cov)

            # =================================================
            # DL models
            # =================================================
            case "rnn":
                series_pred = model.predict(n=len(series_test), future_covariates=series_cov)
            case "tsmixer":
                series_pred = model.predict(n=len(series_test), future_covariates=series_cov)
            case "transformer":
                series_pred = model.predict(n=len(series_test), past_covariates=series_cov)
            case "transformer":
                series_pred = model.predict(n=len(series_test), past_covariates=series_cov)
            case "tft":
                series_pred = model.predict(n=len(series_test), future_covariates=series_cov)
            case "n-beats":
                series_pred = model.predict(n=len(series_test), past_covariates=series_cov)

            case _:
                raise NotImplementedError()

        series_pred = transformer_target.inverse_transform(series_pred)
        # series_pred = transformer.inverse_transform(series_train_diff.concatenate(series_pred)).drop_before(CUTOFF_DATE)

        df = pd.concat(
            [
                series_test.to_dataframe().rename(columns={restaurant: "gt"}),
                series_pred.to_dataframe().rename(columns={restaurant: "pred"})
            ],
            axis=1
        )  # fmt: skip
        df = df[df["gt"] > EPS]
        mape_val = mean_absolute_percentage_error(df["gt"], df["pred"])
    except Exception as e:
        logger.exception(e)

        mape_val = 1e10

    return mape_val


def main():
    args = _parse_args()

    logger.info(f"Restaurant: {args.restaurant}")

    # =================================================
    # Load and process
    # =================================================
    path = "data/processed/waste.parquet"
    waste = pl.read_parquet(path)

    path = "data/processed/dim_restaurants.xlsx"
    dim_restaurants = pl.read_excel(path)

    waste_daily = (
        waste
        .drop('id', 'src')

        .join(
            dim_restaurants.select('restaurant_id', 'restaurant_short'),
            left_on='restaurant',
            right_on='restaurant_id',
            how='left'
        )
        .drop('restaurant')
        .rename({'restaurant_short': 'restaurant'})   


        # Add small amount for training stability
        .with_columns(
            pl.col('waste') + EPS
        )


        # Pivot
        .pivot(index='date', on='restaurant', values='waste')
        .sort('date')

    )  # fmt: skip

    # Make new dataframe only containing entries of weekdays
    waste_daily = (
        pl.DataFrame({
            'date': pl.Series(pd.date_range(waste['date'].min(), waste['date'].max(), freq='B')).cast(pl.Date)
        })

        .join(waste_daily, on='date', how='left')

        .fill_null(EPS)
    )  # fmt: skip

    # Create dim 'exam'
    date_begin = pd.to_datetime(waste_daily["date"].min())
    date_end = pd.to_datetime(waste_daily["date"].max())

    dim_exam = (
        pl
        .from_records([
            {'date_begin': '2023-03-06', 'date_end': '2023-03-12'},  
            {'date_begin': '2023-05-01', 'date_end': '2023-05-07'},
            {'date_begin': '2023-10-23', 'date_end': '2023-10-29'},
            {'date_begin': '2023-12-18', 'date_end': '2023-12-24'},
            {'date_begin': '2024-03-04', 'date_end': '2024-03-10'},
            {'date_begin': '2024-05-06', 'date_end': '2024-05-12'},
            {'date_begin': '2024-10-21', 'date_end': '2024-10-27'},
            {'date_begin': '2025-03-03', 'date_end': '2025-03-09'},
        ])
        .with_columns(
            pl.col('date_begin').str.to_date(),
            pl.col('date_end').str.to_date(),
        )
    )  # fmt: skip

    df = (
        pl.DataFrame()

        # Create blank dataframe with date
        .with_columns(
            pl.date_range(date_begin, date_end, '1d').alias('date')
        )
    )  # fmt: skip

    entries_exam = (
        df
        .join(dim_exam, how='cross')
        .filter(
            (pl.col('date') >= pl.col('date_begin'))
            & (pl.col('date') <= pl.col('date_end'))
        )
        .select(
            'date',
            pl.lit(1).alias('exam')
        )
    )  # fmt: skip
    cov_exam = (
        df
        .join(entries_exam, on='date', how='left')
        .with_columns(
            pl
            .col('exam')
            .fill_null(0)
            .cast(pl.String())
            .cast(pl.Categorical())
        )

        # Remove non-business days
        .filter(pl.col('date').dt.weekday() < 6)
    )  # fmt: skip

    # Create dim holiday
    fin_holidays = holidays.Finland(years=[2023, 2024, 2025])
    dim_holiday = pl.from_records([{"date": d, "name_holiday": n} for d, n in fin_holidays.items()])
    cov_holiday = (
        pl.DataFrame()

        # Create blank dataframe with date
        .with_columns(
            pl.date_range(date_begin, date_end, '1d').alias('date')
        )


        # Add dim holiday
        .join(dim_holiday, on='date', how='left')
        .with_columns(pl.col('name_holiday').is_not_null().cast(pl.Int32).alias('holiday'))
        .drop('name_holiday')


        # Cast to categorical type
        .with_columns(
            pl
            .col('holiday')
            # .cast(pl.String())
            # .cast(pl.Categorical())
        )

        # Remove non-business days
        .filter(pl.col('date').dt.weekday() < 6)
    )  # fmt: skip

    # Create Timeseries instances from tables
    series_exam = TimeSeries.from_dataframe(
        df=cov_exam.to_pandas(), time_col="date", freq="b", fill_missing_dates=False, value_cols="exam"
    )

    series_holiday = TimeSeries.from_dataframe(
        df=cov_holiday.to_pandas(), time_col="date", freq="b", fill_missing_dates=False, value_cols="holiday"
    )

    series = TimeSeries.from_dataframe(
        waste_daily.to_pandas(),
        time_col="date",
        value_cols=args.restaurant,
        fillna_value=EPS,
        freq="B",
    ).astype(np.float32)

    series_cov = series_exam.concatenate(series_holiday, axis=1).astype(np.float32)

    # =================================================
    # Fine-tune
    # =================================================
    # Transform data
    series_train, series_test = series.split_before(CUTOFF_DATE)

    series_train_transformed: TimeSeries = series_train

    transformer_target = Scaler(MinMaxScaler(feature_range=(-1, 1)))
    series_train_transformed = transformer_target.fit_transform(series_train_transformed)

    # Tune
    model_names = [
        "catboost",
        "xgboost",
        "lightbgm",
        "rnn",
        "tsmixer",
        "transformer",
        "tft",
        "n-beats",
    ]
    for model_name in model_names:
        f_objective = partial(
            _f_objective,
            restaurant=args.restaurant,
            model_name=model_name,
            series_train_transformed=series_train_transformed,
            series_test=series_test,
            series_cov=series_cov,
            transformer_target=transformer_target,
        )

        study = optuna.create_study(study_name=model_name)
        study.optimize(f_objective, n_trials=100)

        logger.info(f"{model_name}: best_mape: {study.best_value}: best_params: {study.best_params}")


if __name__ == "__main__":
    sys.exit(main())
