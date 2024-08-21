from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .language_processor import language_processor

MODEL_PATH = "src/data/finalized_model.sav"
SCALER_PATH = "src/data/scaler_model.sav"


class ML_Model:
    def __init__(self, data=None):
        self.data = data
        self.train_x = None
        self.test_x = None
        self.train_y = None
        self.test_y = None
        self.model = None
        self.scaler = StandardScaler()

        self._setup_model()
        self._setup_data()

    def _setup_model(self):
        return None

    def _setup_data(self):
        return None

    def _split_data(self, X, y, test_size=0.2):
        """Split data into training and test data.

        Args:
            X (_type_): feature matrix
            y (_type_): correct value
            test_size (float, optional): Percentage of test data. Defaults to 0.2.
        """
        self.train_x, self.test_x, self.train_y, self.test_y = train_test_split(
            X, y, test_size=test_size, random_state=None, shuffle=True, stratify=None)

    def predict(self, weekday: int, menulist: list):
        """ Get predicted meals sold for day "weekday".
        Takes in the weekday and a list of dishes.

        First is processed by NLP for one hot encoding.
        Also is preprocessed by scaler.

        Returns integer of estimated sold meals.
        """
        data = pd.DataFrame([weekday, menulist], columns=["weekday", "Dish"])
        data["Dish"] = language_processor.process(data["Dish"])

        features = self.scaler.transform(data.values)

        return int(self.model.predict(features)[0])

    def test(self):
        """Test the model. Might present some
        problems if the model is not a neural network.
        
        Can print the prediction and it's errors for more
        of an intuitive look into the error.

        Will return None also due to another function
        expecting three values.

        Returns:
            float: mean absolute error, r2 value
        """
        r2 = self.model.score(self.test_x, self.test_y)

        res = []
        for i in range(len(self.test_x)):
            x = self.scaler.transform(self.test_x[i].reshape(1, -1))
            y = self.test_y[i]
            prediction = self.model.predict(x)
            error = abs(prediction[0] - y)
            res.append(error)
            #print(prediction[0], y, "error: ", error)

        mae = np.array(res).mean()

        return None, mae, r2
