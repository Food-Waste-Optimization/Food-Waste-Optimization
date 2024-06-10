from repositories.data_repository import data_repository
from services.linear_regression import LinearRegressionModel
from services.neural_network import NeuralNetwork

# run with "poetry run python -m src.services.analysis"


class ModelService:
    """Class for handling the connection
    between models and the app.
    """
    def __init__(self):
        self.data = data_repository.roll_means()
        self.model = NeuralNetwork(data=self.data)


    def learn(self):
        self.model.learn()

    def predict(self, feature):
        return self.model.predict(feature)

    def test_model(self):
        self.model.learn()
        return self.model.test()
        #mse, mae, r2 = self.model.test()
        #return f"Mean squared error: {mse}\nMean absolute error: {mae}\nR^2: {r2}"


# HOW TO USE

def example_model():
    s = ModelService()

    s.model.setup_data()

    # After defining the class the model must be fitted using
    
    s.test_model()
    
    # The data is fetched automatically and now it is ready to make predictions

    # Predict using a weekday, e.g. monday = 0, tuesday = 1 ...
    #print(s.predict(2)) # Prediction is a float representing estimated waste for the given day in kgs

    #print(s.test_model()) # this shows info about the accuracy of the model, does not really work yet
    
    #res = []
    #for i in range(0, 1000):
    #    day = i % 7
    #    res.append(s.test_model()[1])
    #print(sum(res)/1000)

    #return s.predict(2)

#print(example_model())
