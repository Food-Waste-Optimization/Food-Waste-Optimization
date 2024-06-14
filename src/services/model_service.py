from ..repositories.data_repository import data_repository
from .linear_regression import LinearRegressionModel
from .neural_network import NeuralNetwork
from sklearn.exceptions import NotFittedError

# run with "poetry run python -m src.services.model_service"


class ModelService:
    """Class for handling the connection
    between models and the app.
    """
    def __init__(self):
        # data is fetched every time init is run, this should not happen
        self.data = data_repository.roll_means()
        self.prediction_data = data_repository.get_df_from_stationary_data()
        self.model = NeuralNetwork(data=self.data, prediction_data=self.prediction_data)
        self.data_repo = data_repository


    def predict(self, feature):
        """This function will predict sold meals
        for a specific day using an offset. Will take a mean
        of last number of days and switches the day to feature.

        Args:
            feature (int): day of prediction, 0 - monday, 1 - tuesday etc.

        Returns:
            int: number of sold meals
        """
        try:
            return self.model.predict(feature)
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
            self.load_model()
        except NotFittedError as err:
            # no model to load
            print("Model could not be loaded, fitting instead:", err)
            self.fit_and_save()
        mse, mae, r2 = self.model.test()

        print(f"Mean squared error: {mse}\nMean absolute error: {mae}\nR^2: {r2}")

    def fit_and_save(self):
        """Will fit the model and the save into a file.
        If unsuccessful, will give error.
        """
        try:
            self.model.fit_and_save()
            print("Model fitted and saved")
        except Exception as err:
            print("Model could not be fitted:", err)

    def load_model(self):
        """This function will load the model. First
        try to load a model and if no model is found,
        will give error.
        """
        try:
            self.model.load_model()
            print("Model loaded")
        except Exception as err:
            print("Model could not be loaded:", err)
    
    def predict_waste_by_day(self, weekday):
        """Predicts food waste for a given day
        based on average food waste per customer
        and estimated amount of customers.

        Args:
            weekday (int): day of week, 0-6

        Returns:
            float: food waste in kgs
        """
        return self.data_repo.get_avg_meals_waste_ratio() * self.predict(weekday=weekday)
    
    def predict_next_week(self, num_of_days=5):
        """Return a list of predictions
        for the next week from current date.

        num_of_days represents the length of week,
        or, how many days the restaurant is open.


        Returns:
            list of int: list of predictions where index is offset from current day
        """
        day_offset = list(range(0, num_of_days))
        return list(map(self.predict, day_offset))
    
    def predict_occupancy(self):
        """Fetches the average occupancy by hour by day by restaurant
        for all restaurants as a dictionary.

        To get occupancy for a given restaurant and day, simply use 
        dict[restaurant_name][day_as_int] = [avg occupancy for hours 0-23]

        Returns:
            dict: above given structure
        """
        return self.data_repo.get_average_occupancy()

# HOW TO USE

def example_model():
    s = ModelService()

    # After defining the class the model must be fitted using
    s.load_model()

    #s.predict(2)

if __name__ == "__main__":
    model = ModelService()
    print(model.predict_occupancy())
    #model.fit_and_save()
    #model.load_model()
    #print(model.predict_next_week(5))
    #model.test_model()
    #predicted_value = model.predict(2)
    #print(predicted_value)
    #print("Saving predicted value to file")
    #with open('src/data/predicted.txt', "w") as file:
    #    file.write(str(predicted_value))
