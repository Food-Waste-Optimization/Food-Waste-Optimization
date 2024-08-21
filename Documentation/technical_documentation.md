# Technical and structural documentation

## General structure
The sourcecode is divided into two separate structures, frontend and backend. Code in the frontend is intended to display the website for the user. There is a "bridge" from the backend to the frontend (_src/app/routes.py_) which is created using Flask. The backend consists of 2 main parts. There is a model for predictions (described later) and a database (schema in _Documentation/db/_). The whole project is run on Megasense server using Docker.

## ML model
- There are currently two possible models to use: Linear Regression and a Neural Network. A NN is used so text input is possible. The linear model is simple and does not need separate explaining. It probably wont work. 

### How the NN works
First the data is fetched from the database (db_repository), then it is combined into a desired dataframe (data_repository). Then, the menu items are encoded as one hot encoding (language processor). Then it is turned into numpy matrices of X (meaning feature matrix) and y (the correct value). Then it is split into training and testing data. 

The matrix consists of one hot encoded menu item and weekday as an integer. Consider using a date as well.

When calling _learn, it will take training data, it will scale it and start fitting. Fitting algos etc. are done by the library itself. 

NeuralNetwork class is a subclass of ML_Model, this is so there can be multiple models efficiently. 

## Model Service
The idea of _model service_ is to be the connection point between frontend and backend (called using the bridge _routes.py_). The routes file will call functions from the model service class and should __not__ call any other class' functions. 

Model service will call functions in the _model's class_ itself(e.g. _NeuralNetwork_). This is so the application does not know which model is used, or how, just gets the values _model service_ provides

The model will then call functions from the class _data_repository_. This class is meant to be the bridge between the application and the database. The database (using _database_repository_) gives "raw" data and the data_repo will process it for the model. 

## Language processor
_Language_processor.py_ uses NLP techiques to process menu items (strings) into lemmas. The lemmas are encoded as numerals using [one-hot-encoding.](https://en.wikipedia.org/wiki/One-hot) This allows the AI model to handle text-based data as well. _Process_learn_ function reads a large set of menu items, saves their encodings to database and returns a list of encodings that correspond to given menu items. _Process_ function reads a smaller set of menu items (a week), fetches their matching encodings from the database and returns a list of the corresponding encodings. 

## Data_repository
The main idea behind data_repository is that the database will store data in a __raw__ format. We must process the data for it to be useful for the model. 

For example, the database gives us data using timestamps, but the model expects them as hourly counts. Data repository will then make the adjustments to the data. It is also easier to make changes this way if, for example, we would want to predict hourly counts instead.

The _data repository_ calls functions from the _database repository_ and is called by _model service_. 

## Database_repository

Module [`db_repository.py`](/src/repositories/db_repository.py) inserts data into and gets it from the PostgreSQL database.

Schemas of the tables can be found in the folder [/schemas](/schemas).

### Restaurant data

For now data from restaurants is uploaded to the database by hand. To make it easier there are functions to insert data from files. Files must be in the correct format.

These functions insert new data into database and keep the old in database.

`insert_biowaste` is used to upload Biowaste data. The CSV file is supposed to have columns

- Date
- Ravintola
- Asiakasbiojäte, tiski (kg)
- Biojäte kahvi, porot (kg)
- Keittiön biojäte (ruoanvalmistus) (kg)
- Salin biojäte (jämät) (kg)

The function is not working properly. If data being inserted contains data that is already in the database, the function will not insert anything into the database. See branch [biowaste-fix](https://github.com/Food-Waste-Optimization/Food-Waste-Optimization/tree/biowaste-fix).

`insert_sold_meals` is used to upload data of sold lunches. The CSV file is supposed to have columns

- Date
- Receipt time
- Restaurant
- Food Category
- Dish
- pcs
- Hiilijalanjälki

The function is working as planned.

The function`insert_restaurants` is called by both `insert_biowaste` and `insert_sold_meals` and the functions `insert_food_categories`and `insert_dishes` are called by the latter. All of these three are working as planned.

**TODO:**

- Fixing of biowaste data insert
- Occupancy from receipts by hour (*Tuntikohtainen asiakasmäärä v2.xlsx*)

### Result data

These functions are supposed to save the results of the predictions etc. to the database. The old data will be deleted when new predictions are saved.

## How to read predictions (TODO)
The server is not fast enough to predict the values on the fly, so we came up with a solution to make the predictions at night automatically. There is a separate container to fit the model and then save it. 

There are specific functions to fetch the predictions from the database in the _model service_ class, but the database functions have not been written yet. 

There needs to be separate function calls to train the model and make predictions (using _model service_) in the separate container automatically. Note: these have not been done yet.



