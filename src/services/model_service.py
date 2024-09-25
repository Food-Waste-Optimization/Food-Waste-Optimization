"""Creates ModelService class that allows requests to AI models."""

import io
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import onnxruntime as rt
import pandas as pd
import seaborn as sns
from darts.models import ARIMA, LightGBMModel, LinearRegressionModel
from loguru import logger
from xgboost import XGBRegressor

RESTAURANTS = ["Chemicum", "Physicum", "Exactum"]
NUM_TIMESTAMP_PER_DAY = (
    9  # Since each day, the predictions' timestamp are 10 AM, 11 AM... 15 PM
)


class ModelService:
    """Class for handling the connection between models, data and the app."""

    PATH_ROOT_TRAINED_MODEL = Path("/trained_models")

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
        }
        self._load_receipt_forecaster()
        self._load_biowaste_forecaster()
        self._load_occupancy_forecaster()
        self._load_meal_forecaster()

        self._load_receipt_byday_forecaster()
        self._load_biowaste_from_meal_forecaster()
        self._load_co2_from_meal_forecaster()

        plt.style.use("seaborn-v0_8")
        plt.rcParams.update({"font.size": 8})

        # self.data = data_repo.get_model_fit_data()
        # self.model = NeuralNetwork(
        #     data=self.data)

    def _load_receipt_forecaster(self):
        logger.info("Load trained receipt forecasting models for 3 restaurants")

        model_name = "receipt"
        add_encoders = {
            "cyclic": {"future": ["hour", "dayofweek"]},
            "datetime_attribute": {"future": ["hour", "dayofweek"]},
        }

        for restaurant in RESTAURANTS:
            path_model = (
                ModelService.PATH_ROOT_TRAINED_MODEL / model_name / f"{restaurant}.pt"
            )
            self.models[model_name][restaurant] = ARIMA(add_encoders=add_encoders).load(
                path_model
            )

    def _load_biowaste_forecaster(self):
        logger.info("Load trained biowaste forecasting models for 3 restaurants")

        add_encoders = {
            "cyclic": {"past": ["dayofweek"]},
            "datetime_attribute": {"past": ["dayofweek"]},
        }
        model_name = "biowaste"

        for restaurant in RESTAURANTS:
            path_model = (
                ModelService.PATH_ROOT_TRAINED_MODEL / model_name / f"{restaurant}.pt"
            )
            self.models[model_name][restaurant] = LinearRegressionModel(
                lags=5, lags_past_covariates=5, add_encoders=add_encoders
            ).load(path_model)

    def _load_occupancy_forecaster(self):
        logger.info("Load trained occupancy forecasting models for 3 restaurants")

        model_name = "occupancy"
        add_encoders = {
            "cyclic": {"future": ["hour", "dayofweek"]},
            "datetime_attribute": {"future": ["hour", "dayofweek"]},
        }

        for restaurant in RESTAURANTS:
            path_model = (
                ModelService.PATH_ROOT_TRAINED_MODEL / model_name / f"{restaurant}.pt"
            )
            self.models[model_name][restaurant] = ARIMA(add_encoders=add_encoders).load(
                path_model
            )

    def _load_meal_forecaster(self):
        logger.info("Load trained meal forecasting models for 3 restaurants")

        add_encoders = {
            "cyclic": {"past": ["dayofweek"]},
            "datetime_attribute": {"past": ["dayofweek"]},
        }
        model_name = "meal"

        for restaurant in RESTAURANTS:
            path_model = (
                ModelService.PATH_ROOT_TRAINED_MODEL / model_name / f"{restaurant}.pt"
            )
            self.models[model_name][restaurant] = LinearRegressionModel(
                lags=4, lags_past_covariates=5, add_encoders=add_encoders
            ).load(path_model)

    def _load_receipt_byday_forecaster(self):
        logger.info("Load trained receipt forecasting model by day")

        add_encoders = {
            "cyclic": {"future": ["dayofweek", "day", "month"]},
            "datetime_attribute": {"future": ["dayofweek", "day", "month"]},
        }
        path_model = Path("trained_models/receipt/Jul_23_LightBGM.pt")

        self.models["receipt_per_day"] = LightGBMModel(
            lags=7,
            lags_future_covariates=[0],
            add_encoders=add_encoders,
            output_chunk_length=1,
            verbose=-1,
        ).load(path_model)

    def _load_biowaste_from_meal_forecaster(self):
        logger.info("Load trained biowaste from meal forecasting models by restaurant")

        for restaurant in RESTAURANTS:
            path_model = (
                ModelService.PATH_ROOT_TRAINED_MODEL
                / f"biowaste/Jul24_Lasso_{restaurant}.onnx"
            )

            self.models["biowaste_from_meal"][restaurant] = rt.InferenceSession(
                path_model, providers=["CPUExecutionProvider"]
            )

    def _load_co2_from_meal_forecaster(self):
        logger.info("Load trained co2 from meal forecasting models by restaurant")

        for restaurant in RESTAURANTS:
            path_model = (
                ModelService.PATH_ROOT_TRAINED_MODEL
                / f"co2/Aug21_XGBoost_{restaurant}.json"
            )

            assert path_model.exists()

            regressor = XGBRegressor()
            regressor.load_model(path_model)
            self.models["co2_from_meal"][restaurant] = regressor

    def _post_process(self, prediction):
        if prediction <= 0:
            prediction = 0.0

        prediction = round(prediction, 2)

        return prediction

    def forecast_receipt(self, num_of_days: int = 5) -> list:
        """Forecast the number of receipts `num_of_days` ahead

        Args:
            num_of_days (int, optional): The number of days for forecasting. Defaults to 5.

        Returns:
            list: forecasted receipt quantity per date per restaurant
        """

        predictions = pd.DataFrame()

        # Forecast the future
        for restaurant in RESTAURANTS:
            pred = self.models["receipt"][restaurant].predict(
                num_of_days * NUM_TIMESTAMP_PER_DAY
            )

            if len(predictions) == 0:
                predictions["datetime"] = pred.time_index

            predictions.loc[:, restaurant] = [
                self._post_process(x) for x in pred.values().squeeze().tolist()
            ]

        # Post-process
        predictions["datetime"] = predictions["datetime"].dt.strftime(
            r"%Y-%m-%d %H:%M:%S"
        )

        # Return
        ret = predictions.to_dict("records")

        return ret

    def forecast_biowaste(self, num_of_days: int = 5):
        predictions = {}

        # Forecast the future
        for restaurant in RESTAURANTS:
            pred = self.models["biowaste"][restaurant].predict(num_of_days)

            df_pred = pred.pd_dataframe().reset_index()
            df_pred["date"] = df_pred["date"].dt.strftime(r"%Y-%m-%d")

            for row in df_pred.itertuples():
                if row.date not in predictions:
                    predictions[row.date] = {"date": row.date}

                predictions[row.date] = {
                    **predictions[row.date],
                    restaurant: {
                        "amnt_waste_customer": self._post_process(
                            row.amnt_waste_customer
                        ),
                        "amnt_waste_coffee": self._post_process(row.amnt_waste_coffee),
                        "amnt_waste_kitchen": self._post_process(
                            row.amnt_waste_kitchen
                        ),
                        "amnt_waste_hall": self._post_process(row.amnt_waste_hall),
                    },
                }

        # Return
        ret = list(predictions.values())

        return ret

    def forecast_occupancy(self, num_of_days: int = 5) -> list:
        """Forecast the number of occupancy from SuperSight data

        Args:
            num_of_days (int, optional): _description_. Defaults to 5.
        """
        num_timesteps = NUM_TIMESTAMP_PER_DAY * num_of_days

        predictions = {}
        for restaurant in RESTAURANTS:
            # Forecast
            pred = self.models["occupancy"][restaurant].predict(num_timesteps)

            # Post-process forecasted data
            df_pred = pred.pd_dataframe().reset_index()
            df_pred["datetime"] = df_pred["datetime"].dt.strftime(r"%Y-%m-%d %H:%M:%S")

            for row in df_pred.itertuples():
                if row.datetime not in predictions:
                    predictions[row.datetime] = {"datetime": row.datetime}

                predictions[row.datetime][restaurant] = self._post_process(
                    row.num_customer_in
                )

        ret = list(predictions.values())

        return ret

    def forecast_sold_meals(self, num_of_days: int = 5):
        predictions = {}

        # Forecast the future
        for restaurant in RESTAURANTS:
            pred = self.models["meal"][restaurant].predict(num_of_days)

            df_pred = pred.pd_dataframe().reset_index()
            df_pred["date"] = df_pred["date"].dt.strftime(r"%Y-%m-%d")

            for row in df_pred.itertuples():
                if row.date not in predictions:
                    predictions[row.date] = {"date": row.date}

                predictions[row.date] = {
                    **predictions[row.date],
                    restaurant: {
                        "num_fish": self._post_process(row.num_fish),
                        "num_chicken": self._post_process(row.num_chicken),
                        "num_vegetable": self._post_process(row.num_vegetable),
                        "num_meat": self._post_process(row.num_meat),
                        "num_NotMapped": self._post_process(row.num_NotMapped),
                        "num_vegan": self._post_process(row.num_vegan),
                    },
                }

        # Return
        ret = list(predictions.values())

        return ret

    def forecast_biowaste_with_meal(
        self,
        restaurant: str,
        num_fish: float,
        num_chicken: float,
        num_vegetarian: float,
        num_meat: float,
        num_vegan: float,
        date: str,
        return_type: str,
    ):
        # Predict no. receipts next day
        date_pred = pd.to_datetime(date)

        # Ensure the predicted day is not weekend
        if date_pred.weekday() >= 5:
            raise ValueError("Input date must not be weekend")

        # Ensure the date must be greater or equal to '2024-05-09
        DATE_FIRST_PREDICT = (
            "2024-05-09"  # The day after the last available date in data
        )
        n_bdays = len(pd.bdate_range(start=DATE_FIRST_PREDICT, end=date_pred))
        if n_bdays <= 0:
            raise ValueError("Input date not after 2024-05-08")

        out = self.models["receipt_per_day"].predict(n_bdays)

        # logger.info(f"date_pred: {out.time_index[-1]}")

        n_rpts = (
            out[f"{restaurant}_rcpts"]
            .data_array()[-1]
            .to_numpy()
            .squeeze()
            .astype(np.int32)
            .item()
        )

        # Predict waste
        X_predict = pd.DataFrame(
            {
                "fish": [num_fish],
                "chicken": [num_chicken],
                "vegetarian": [num_vegetarian],
                "meat": [num_meat],
                "vegan": [num_vegan],
            }
        )

        sess = self.models["biowaste_from_meal"][restaurant]
        input_name = sess.get_inputs()[0].name
        label_name = sess.get_outputs()[0].name
        pred_onx = sess.run([label_name], {input_name: X_predict.to_numpy()})[0]

        # Calculate the waste per customer
        amnt_waste_per_customer = pred_onx.sum() * 1000 / n_rpts

        ret = None
        if return_type == "image":
            # Plot
            fig = plt.figure(figsize=(10, 8))
            fig.suptitle(f"Forecast in date: {date}", fontweight="bold", fontsize=14)

            ax = fig.add_subplot(221)
            sns.barplot(X_predict, ax=ax)
            for i, val in enumerate(X_predict.to_numpy().squeeze().astype(np.int32)):
                plt.text(i, val + 2, val, ha="center", fontsize=11)
            ax.set_title("Input: number of meals per type", fontweight="bold")

            ax = fig.add_subplot(222)
            sns.barplot(x=["Customer", "Kitchen"], y=pred_onx.squeeze(), ax=ax)
            for i, val in enumerate(pred_onx.squeeze()):
                plt.text(i, val + 0.2, f"{val:.2f}", ha="center", fontsize=11)
            ax.set_title("Predicted amount of waste per type", fontweight="bold")

            ax = fig.add_subplot(223)
            sns.barplot(x=["Num. receipts"], y=[n_rpts], ax=ax)
            ax.set_title("Forecasted number of receipts (POS)", fontweight="bold")

            ax = fig.add_subplot(224)
            sns.barplot(x=["Amount"], y=[amnt_waste_per_customer], ax=ax)
            ax.axhline(y=40, color="r", linestyle="-.")
            ax.set_title("Amnt. waste per customer (in gram)", fontweight="bold")

            # Export image
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)

            ret = buf.read()
        elif return_type == "numeric":
            ret = {
                "date": date,
                "predicted_waste_customer": pred_onx.squeeze()[0].item(),
                "predicted_waste_kitchen": pred_onx.squeeze()[1].item(),
                "predicted_num_receipts": n_rpts,
                "predicted_waste_per_customer": amnt_waste_per_customer.item(),
            }
        else:
            raise NotImplementedError

        return ret

    def forecast_co2_with_meal(
        self,
        restaurant: str,
        num_fish: float,
        num_chicken: float,
        num_vegetarian: float,
        num_meat: float,
        num_vegan: float,
    ):
        # Predict co2
        X_predict = np.array(
            [
                [
                    num_fish,
                    num_chicken,
                    num_vegetarian,
                    num_meat,
                    num_vegan,
                ]
            ],
            dtype=np.float32,
        )

        model = self.models["co2_from_meal"][restaurant]

        pred_co2 = model.predict(X_predict)

        ret = {
            "predicted_co2": pred_co2.squeeze().item(),
        }

        return ret
