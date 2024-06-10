from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MODEL_PATH = "src/data/finalized_model.sav"
SCALER_PATH = "src/data/scaler_model.sav"

class ML_Model:
    def __init__(self, data, prediction_data):
        self.data = data
        self.prediction_data = prediction_data
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
    
    def _split_data(self, X, y, test_size=0.1):
        self.train_x, self.test_x, self.train_y, self.test_y = train_test_split(X, y, test_size=test_size, random_state=None, shuffle=True, stratify=None)
    
    def predict(self, weekday=0):
        """ Get predicted meals sold for day "weekday".
        Uses average of last "x" days as input data.
        """
        features = self.get_avg_of_last_days().values

        features[-1] = weekday

        features = self.scaler.transform(features)

        return int(self.model.predict(features)[0])

    def get_avg_of_last_days(self, days=5):
        """
        Get the average of all numeric features of the last `days` days.
        In theory, this will give the model a better capability of predicting 
        according to larger trends than just the previous day.

        Default is 5 days.

        Returns: DataFrame of one entry which is the average of the last `days` days.
        """
        df = self.prediction_data.iloc[-days:].reset_index(drop=True)
        
        # Convert all columns to numeric, coercing errors to NaN
        df = df.apply(pd.to_numeric, errors='coerce')
        
        # Compute the mean, skipping NaN values
        numeric_avg = df.mean(axis=0, skipna=True)
        
        return pd.DataFrame(numeric_avg).T


    def test(self):
        r2 = self.model.score(self.test_x, self.test_y)

        res = []
        for i in range(len(self.test_x)):
            x = self.scaler.transform(self.test_x[i].reshape(1,-1))
            y = self.test_y[i]
            prediction = self.model.predict(x)
            error = abs(prediction[0] - y)
            res.append(error)
            #print(prediction[0], y, "error: ", error)
        
        mae = np.array(res).mean()

        return None, mae, r2
