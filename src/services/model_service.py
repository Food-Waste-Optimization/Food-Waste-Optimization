"""Creates ModelService class that allows requests to AI models."""
from pathlib import Path

import pandas as pd
from darts.models import ARIMA, LinearRegressionModel
from loguru import logger
from sklearn.exceptions import NotFittedError

from ..repositories.data_repository import data_repo

# run with "poetry run python -m src.services.model_service"

RESTAURANTS = ['Chemicum', 'Physicum', 'Exactum']
NUM_TIMESTAMP_PER_DAY = 9   # Since each day, the predictions' timestamp are 10 AM, 11 AM... 15 PM
path_root_trained_model = Path("trained_models")

class ModelService:
    """Class for handling the connection
    between models, data and the app.
    """

    def __init__(self):
        # data is fetched every time init is run, this should not happen\
        self.models = {
            'receipt': {},
            'biowaste': {},
            'occupancy': {},
            'meal': {},
        }
        self._load_receipt_forecaster()
        self._load_biowaste_forecaster()
        self._load_occupancy_forecaster()
        self._load_meal_forecaster()

        # self.data = data_repo.get_model_fit_data()
        # self.model = NeuralNetwork(
        #     data=self.data)

    def _load_receipt_forecaster(self):
        logger.info("Load trained receipt forecasting models for 3 restaurants")

        model_name = "receipt"
        add_encoders = {
            'cyclic': {
                'future': ['hour', 'dayofweek']
            },
            'datetime_attribute': {'future': ['hour', 'dayofweek']},
        }

        for restaurant in RESTAURANTS:
            path_model = path_root_trained_model / model_name / f"{restaurant}.pt"
            self.models[model_name][restaurant] = ARIMA(add_encoders=add_encoders).load(path_model)
                
    def _load_biowaste_forecaster(self):
        logger.info("Load trained biowaste forecasting models for 3 restaurants")

        add_encoders = {
            'cyclic': {
                'past': ['dayofweek']
            },
            'datetime_attribute': {'past': ['dayofweek']},
        }
        model_name = "biowaste"

        for restaurant in RESTAURANTS:
            path_model = path_root_trained_model / model_name / f"{restaurant}.pt"
            self.models[model_name][restaurant] = LinearRegressionModel(lags=5, lags_past_covariates=5, add_encoders=add_encoders).load(path_model)

    def _load_occupancy_forecaster(self):
        logger.info("Load trained occupancy forecasting models for 3 restaurants")

        model_name = "occupancy"
        add_encoders = {
            'cyclic': {
                'future': ['hour', 'dayofweek']
            },
            'datetime_attribute': {'future': ['hour', 'dayofweek']},
        }

        for restaurant in RESTAURANTS:
            path_model = path_root_trained_model / model_name / f"{restaurant}.pt"
            self.models[model_name][restaurant] = ARIMA(add_encoders=add_encoders).load(path_model)

    def _load_meal_forecaster(self):
        logger.info("Load trained meal forecasting models for 3 restaurants")

        add_encoders = {
            'cyclic': {
                'past': ['dayofweek']
            },
            'datetime_attribute': {'past': ['dayofweek']},
        }
        model_name = "meal"

        for restaurant in RESTAURANTS:
            path_model = path_root_trained_model / model_name / f"{restaurant}.pt"
            self.models[model_name][restaurant] = LinearRegressionModel(lags=4, lags_past_covariates=5, add_encoders=add_encoders).load(path_model)

    def _post_process(self, prediction):
        if prediction <= 0:
            prediction = 0.

        prediction = round(prediction, 2)

        return prediction

    def __predict(self, weekday: int, meal_plan: list):
        """This function will predict sold meals
        for a specific day and meal plan
        Args:
            weekday (int): day of prediction, 0 - monday, 1 - tuesday etc.
            meal_plan (list): dishes to be sold on that day
        Returns:
            int: number of sold meals
        """
        try:
            return self.model.predict(weekday=weekday, dishes=meal_plan)
        except NotFittedError:
            print("You must load or fit model first")

    def test_model(self):
        """First will try to load model, if unsuccessful,
        will fit and save a model. Then will run tests

        prints:
        Mean squared error
        Mean absolute error
        R^2 value
        """
        try:
            self.load_model()
        except NotFittedError as err:
            # no model to load
            print("Model could not be loaded, fitting instead:", err)
            self.fit_and_save()
        mse, mae, r2 = self.model.test()

        print(
            f"Mean squared error: {mse}\nMean absolute error: {mae}\nR^2: {r2}")

    def fit_and_save(self):
        """Will fit the model and the save into a file.
        If unsuccessful, will give error.
        """
        try:
            print("Fitting model")
            self.model.fit_and_save()
            print("Model fitted and saved")
        except Exception as err: # pylint: disable=W0718
            print("Model could not be fitted:", err)

    def load_model(self):
        """This function will load the model. First
        try to load a model and if no model is found,
        will give error.
        """
        try:
            self.model.load_model()
            print("Model loaded")
        except Exception as err: # pylint: disable=W0718
            print("Model could not be loaded:", err)

    def _predict_waste_by_week(self):
        """Predicts food waste for a week
        based on average food waste per customer
        and estimated amount of customers.

        Saves prediction to permanent storage
        and should be fetched from there.
        """
        waste = data_repo.get_avg_meals_waste_ratio()
        for waste_type in waste:
            for restaurant, weight in waste[waste_type].items():
                waste[waste_type][restaurant] = list(
                    map(lambda i: i*weight, self._predict_next_week()))
                
        data_repo.save_latest_biowaste_prediction(waste)

    def _predict_next_week(self, num_of_days: int, menu_plan: list):
        """Return a list of predictions
        for the next week from current date.

        num_of_days represents the length of week,
        or, how many days the restaurant is open.

        menu_plan represents the menus for the days.
        It should be a list of lists. The main list for each day
        and inner list for each dish.

        Data struct:
            list of int: list of predictions where index is offset from current day

        Is saved to permanent storage.
        """
        day_offset = list(range(0, num_of_days))
        pred = list(map(self.__predict, day_offset, menu_plan))
        data_repo.save_latest_weekly_prediction(pred)
    
    def get_latest_weekly_prediction(self):
        """Will use data_repository to fetch the latest
        prediction of sold meals stored in a desired place. Currently
        in a database. Is necessary to allow faster load
        times for the website.

        This should be used by the routes function.
        """
        return data_repo.get_latest_weekly_prediction()

    def get_biowaste_prediction(self):
        """Will use data_repository to fetch the latest
        biowaste prediction stored in a desired place. Currently
        in a database. Is necessary to allow faster load
        times for the website.
        
        This should be used by the routes function.
        """
        return data_repo.get_latest_biowaste_prediction()

    def get_occupancy_prediction(self):
        """Will use data_repository to fetch the latest
        prediction of occupancy stored in a desired place. Currently
        in a database. Is necessary to allow faster load
        times for the website.
        
        This should be used by the routes function.
        """
        return data_repo.get_latest_occupancy_prediction()
    



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
            pred = self.models['receipt'][restaurant].predict(num_of_days * NUM_TIMESTAMP_PER_DAY)

            if len(predictions) == 0:
                predictions['datetime'] = pred.time_index

            predictions.loc[:, restaurant] = [self._post_process(x) for x in pred.values().squeeze().tolist()]

        # Post-process
        predictions['datetime'] = predictions['datetime'].dt.strftime(r"%Y-%m-%d %H:%M:%S")

        # Return
        ret = predictions.to_dict('records')

        return ret
    
    def forecast_biowaste(self, num_of_days: int = 5):        
        predictions = {}

        # Forecast the future
        for restaurant in RESTAURANTS:
            pred = self.models['biowaste'][restaurant].predict(num_of_days)

            df_pred = pred.pd_dataframe().reset_index()
            df_pred['date'] = df_pred['date'].dt.strftime(r"%Y-%m-%d")

            for row in df_pred.itertuples():
                if row.date not in predictions:
                    predictions[row.date] = {
                        'date': row.date
                    }

                predictions[row.date] = {
                    **predictions[row.date],
                    restaurant: {
                        'amnt_waste_customer': self._post_process(row.amnt_waste_customer),
                        'amnt_waste_coffee': self._post_process(row.amnt_waste_coffee),
                        'amnt_waste_kitchen': self._post_process(row.amnt_waste_kitchen),
                        'amnt_waste_hall': self._post_process(row.amnt_waste_hall),
                    }
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
            pred = self.models['occupancy'][restaurant].predict(num_timesteps)

            # Post-process forecasted data
            df_pred = pred.pd_dataframe().reset_index()
            df_pred['datetime'] = df_pred['datetime'].dt.strftime(r"%Y-%m-%d %H:%M:%S")

            for row in df_pred.itertuples():
                if row.datetime not in predictions:
                    predictions[row.datetime] = {'datetime': row.datetime}

                predictions[row.datetime][restaurant] = self._post_process(row.num_customer_in)

        ret = list(predictions.values())

        return ret

    def forecast_sold_meals(self, num_of_days: int = 5):
        predictions = {}

        # Forecast the future
        for restaurant in RESTAURANTS:
            pred = self.models['meal'][restaurant].predict(num_of_days)

            df_pred = pred.pd_dataframe().reset_index()
            df_pred['date'] = df_pred['date'].dt.strftime(r"%Y-%m-%d")

            for row in df_pred.itertuples():
                if row.date not in predictions:
                    predictions[row.date] = {
                        'date': row.date
                    }

                predictions[row.date] = {
                    **predictions[row.date],
                    restaurant: {
                        'num_fish': self._post_process(row.num_fish),
                        'num_chicken': self._post_process(row.num_chicken),
                        'num_vegetable': self._post_process(row.num_vegetable),
                        'num_meat': self._post_process(row.num_meat),
                        'num_NotMapped': self._post_process(row.num_NotMapped),
                        'num_vegan': self._post_process(row.num_vegan),
                    }
                }

        # Return
        ret = list(predictions.values())

        return ret


if __name__ == "__main__":
    model = ModelService()
    model.fit_and_save()
    model.test_model()
    
