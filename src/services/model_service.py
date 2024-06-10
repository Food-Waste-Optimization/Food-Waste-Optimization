from src.repositories.data_repository import data_repository
from src.services.linear_regression import LinearRegressionModel
from src.services.neural_network import NeuralNetwork
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

    def predict(self, feature):
        try:
            return self.model.predict(feature)
        except NotFittedError as err:
            print("You must load or fit model first")

    def test_model(self):
        try:
            self.load_model()
        except NotFittedError as err:
            # no model to load
            print("Model could not be loaded, fitting instead:", err)
            self.fit_and_save()
        mse, mae, r2 = self.model.test()

        print(f"Mean squared error: {mse}\nMean absolute error: {mae}\nR^2: {r2}")

    def fit_and_save(self):
        try:
            self.model.fit_and_save()
            print("Model fitted and saved")
        except Exception as err:
            print("Model could not be fitted:", err)

    def load_model(self):
        try:
            self.model.load_model()
            print("Model loaded")
        except Exception as err:
            print("Model could not be loaded:", err)
            self.model.fit_and_save()

# HOW TO USE

def example_model():
    s = ModelService()

    # After defining the class the model must be fitted using
    s.load_model()

    #s.predict(2)

if __name__ == "__main__":
    model = ModelService()
    model.fit_and_save()
    model.load_model()
    model.test_model()
    print(model.predict(2))
