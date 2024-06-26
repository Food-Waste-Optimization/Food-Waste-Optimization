#from src.services.ml_model import ML_Model, MODEL_PATH, SCALER_PATH
from .ml_model import ML_Model, MODEL_PATH, SCALER_PATH
from sklearn.neural_network import MLPRegressor
from matplotlib import pyplot as plt
import pickle


class NeuralNetwork(ML_Model):
    """Multilayer Perceptron doing
    regression.
    """

    def _setup_model(self):
        self.model = MLPRegressor(hidden_layer_sizes=(500, 250),
                                  batch_size=5,
                                  activation="relu",
                                  solver="adam",
                                  learning_rate="invscaling",
                                  learning_rate_init=0.1,
                                  max_iter=1_00,
                                  early_stopping=False,
                                  shuffle=True)

    def _setup_data(self):
        y = self.data["sold meals"].values
        X = self.data.drop("sold meals", axis="columns").values

        self._split_data(X, y)

    def _learn(self, show_curve=False):
        """Function to fit the model to the
        training data.

        Args:
            show_curve (bool, optional): If true shows loss curve. Defaults to False.
        """
        print("learn function start")
        self.train_x = self.scaler.fit_transform(self.train_x)

        self.model.fit(X=self.train_x, y=self.train_y)

        print("Best loss:", self.model.best_loss_)

        if show_curve:
            plt.plot(range(len(self.model.loss_curve_)),
                     self.model.loss_curve_)
            plt.show()

    def fit_and_save(self):
        """Function to first fit the model
        and then save it along with its scaler
        for preprocessing.
        """
        self._learn()
        pickle.dump(self.model, open(MODEL_PATH, 'wb'))
        pickle.dump(self.scaler, open(SCALER_PATH, 'wb'))

    def load_model(self):
        """Function to load a saved model (and scaler)
        from a file.
        """
        self.model = pickle.load(open(MODEL_PATH, 'rb'))
        self.scaler = pickle.load(open(SCALER_PATH, 'rb'))
