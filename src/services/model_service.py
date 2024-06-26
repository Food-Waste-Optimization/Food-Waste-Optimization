"""Creates ModelService class that allows requests to AI models."""
from pathlib import Path

import pandas as pd
from darts.models import ARIMA
from loguru import logger
from sklearn.exceptions import NotFittedError

from ..repositories.data_repository import data_repo
from .neural_network import NeuralNetwork

# run with "poetry run python -m src.services.model_service"

RESTAURANTS = ['600 Chemicum', '610 Physicum', '620 Exactum']
path_root_trained_model = Path("trained_models")
timestep_per_day = 9    # [8 AM, 9 AM, ... 16 PM]

class ModelService:
    """Class for handling the connection
    between models, data and the app.
    """

    def __init__(self):
        # data is fetched every time init is run, this should not happen

        # FIXME: HoangLe [Jun-25]: These 3 below are disabled for testing purpose. They are enabled by default
        # self.data = data_repo.get_model_fit_data()
        # self.predictor_data = data_repo.get_model_predict_data()
        # self.model = NeuralNetwork(data=self.data, prediction_data=self.prediction_data)


        # self.data = data_repo.get_model_fit_data()

        # # predict data is not currently used
        # self.predictor_data = data_repo.get_model_predict_data()

        # self.model = NeuralNetwork(
        #     data=self.data, prediction_data=self.prediction_data)

        self.models = {}
        self._load_arima()

    def _load_arima(self):
        logger.info("Load trained ARIMA models for 3 restaurants")

        model_name = "ARIMA"
        add_encoders = {
            'cyclic': {
                'future': ['hour', 'dayofweek']
            },
            'datetime_attribute': {'future': ['hour', 'dayofweek']},
        }

        for restaurant in RESTAURANTS:
            path_arima = path_root_trained_model / model_name / f"{restaurant}.pt"
            self.models[restaurant] = ARIMA(add_encoders=add_encoders).load(path_arima)
        


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
        except NotFittedError as err:
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
            self.__load_model()
        except NotFittedError as err:
            # no model to load
            print("Model could not be loaded, fitting instead:", err)
            self.__fit_and_save()
        mse, mae, r2 = self.model.test()

        print(
            f"Mean squared error: {mse}\nMean absolute error: {mae}\nR^2: {r2}")

    def __fit_and_save(self):
        """Will fit the model and the save into a file.
        If unsuccessful, will give error.
        """
        try:
            self.model.fit_and_save()
            print("Model fitted and saved")
        except Exception as err: # pylint: disable=W0718
            print("Model could not be fitted:", err)

    def __load_model(self):
        """This function will load the model. First
        try to load a model and if no model is found,
        will give error.
        """
        try:
            self.model.load_model()
            print("Model loaded")
        except Exception as err: # pylint: disable=W0718
            print("Model could not be loaded:", err)

    def __predict_waste_by_week(self):
        """Predicts food waste for a week
        based on average food waste per customer
        and estimated amount of customers.

        Should be modified. End result should be where
        restaurant prediction is mapped to meal waste ratio prediction.

        Returns:
            float: food waste in kgs
        """
        waste = self.data_repo.get_avg_meals_waste_ratio()
        for waste_type in waste:
            for restaurant, weight in waste[waste_type].items():
                waste[waste_type][restaurant] = list(
                    map(lambda i: i*weight, self.__predict_next_week()))
        return waste

    def __predict_next_week(self, num_of_days: int, menu_plan: list):
        """Return a list of predictions
        for the next week from current date.

        num_of_days represents the length of week,
        or, how many days the restaurant is open.

        menu_plan represents the menus for the days.
        It should be a list of lists. The main list for each day
        and inner list for each dish.

        Returns:
            list of int: list of predictions where index is offset from current day
        """
        day_offset = list(range(0, num_of_days))
        return list(map(self.__predict, day_offset, menu_plan))

    def predict_occupancy(self, num_of_days: int = 5):
        """Fetches the average occupancy by hour by day by restaurant
        for all restaurants as a dictionary.

        To get occupancy for a given restaurant and day, simply use
        dict[restaurant_name][day_as_int] = [avg occupancy for hours 0-23]

        Returns:
            dict: above given structure
        """

        # return self.data_repo.get_average_occupancy()
        
        predictions = pd.DataFrame()

        # Forecast the future
        for restaurant in RESTAURANTS:
            pred = self.models[restaurant].predict(num_of_days * timestep_per_day)

            if len(predictions) == 0:
                predictions['datetime'] = pred.time_index

            predictions.loc[:, restaurant] = pred.values()

        # Post-process
        predictions['datetime'] = predictions['datetime'].dt.strftime(r"%Y-%m-%d %H:%M:%S")

        # Return
        ret = predictions.to_dict('records')

        return ret
        return self.data_repo.get_average_occupancy()
    
    def get_latest_weekly_prediction(self):
        """Will use data_repository to fetch the latest
        prediction of sold meals stored in a desired place. Currently
        in a database. Is necessary to allow faster load
        times for the website.
        """
        pass

    def get_latest_biowaste_prediction(self):
        """Will use data_repository to fetch the latest
        biowaste prediction stored in a desired place. Currently
        in a database. Is necessary to allow faster load
        times for the website."""
        pass

    def get_latest_occupancy_prediction(self):
        """Will use data_repository to fetch the latest
        prediction of occupancy stored in a desired place. Currently
        in a database. Is necessary to allow faster load
        times for the website."""
        pass



# HOW TO USE


def example_model():
    """Creates an instance of ModelService for accessing the class methods."""
    s = ModelService()

    # After defining the class the model must be fitted using
    s.load_model()

    # s.predict(2)


if __name__ == "__main__":
    model = ModelService()
    model.__fit_and_save()
    #model.load_model()
    #print(model.predict_waste_by_week())
    # print(model.predict_next_week(5))
    # model.test_model()
    # predicted_value = model.predict(2)
    # print(predicted_value)
    # print("Saving predicted value to file")
    # with open('src/data/predicted.txt', "w") as file:
    #    file.write(str(predicted_value))
