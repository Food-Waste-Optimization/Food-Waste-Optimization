from services.ml_model import ML_Model
from sklearn.linear_model import LinearRegression

class LinearRegressionModel(ML_Model):
    """Class for linear regression. Uses
    sklearn model.
    """
    def _setup_model(self):
        self.model = LinearRegression(fit_intercept=True, positive=False, copy_X=True)

    def _learn(self):
        y = self.data["620 Exactum"]
        X = self.data.drop("620 Exactum", axis="columns")

        self.split_data(X, y)
        
        self.train_x = self.scaler.fit_transform(self.train_x)
        
        self.model.fit(X=self.train_x, y=self.train_y)

