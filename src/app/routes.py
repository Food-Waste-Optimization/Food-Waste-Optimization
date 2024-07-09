import pandas as pd
from flask import jsonify, make_response, render_template, request

from src.services import model_service

from ..app.app import app

""" 
    All the routes the app uses are defined here. Data is accessed through the ModelService
    Currently imports and load_model() are off -> switch these on once the database is running.
    Once database is in use, import for pandas is not needed anymore.
"""

model = model_service.ModelService()

# model = model_service.ModelService()
# model.load_model()

# == APIs for Others ===================================================================================================================

"""Route for testing database connection. 
    Returns:
        Can be used to return test data
"""
@app.route("/dbtest")
def db_conn_test():
    return "not testing database connection"

"""Root URL. Currently does not return anything while running locally - use localhost:8080 instead to access front end.
    While running on server returns the static files of React build - version. See configuration on app.py.
    Returns:
        Static html-file: React build version located on frontend/dist.
"""
@app.route("/")
@app.route("/fwowebserver")
def initial_view():
    resp = make_response(render_template('index.html'))
    resp.headers['Accept-Ranges'] = 'none'

    return resp

"""URL for testing returning prediction data.
    Returns:
        JSON: Object containing prediction from predicted.txt. 
"""
@app.route('/api/data')
def get_data_for_wednesday():
    with open('src/data/predicted.txt', mode='r') as file:
        prediction = file.readline()
        return jsonify({'content': prediction })

"""URL for GET requests of data of occupancy. 
    Returns:
        JSON: Json Object containing data of occupancy of different restaurants
"""

# == APIs for Prediction ===================================================================================================================
@app.route('/data/receipts')
def forecast_receipt():
    resp = None

    # Request checking
    days_raw = request.args.get('days')
    if days_raw is None:
        resp = make_response("Invalid query argument: 'days'", 400)
        

    if resp is None:
        assert days_raw

        try:
            days = int(days_raw)
        except Exception as e:
            # tb = traceback.format_exc()

            resp = make_response(f"Error with query argument 'days': {e}", 400)
    
    if resp is None:
        data = model.forecast_receipt(days)

        resp = make_response(jsonify(data), 200)
    
    return resp

@app.route('/data/biowaste')
def forecast_biowaste():
    resp = None

    # Request checking
    days_raw = request.args.get('days')
    if days_raw is None:
        resp = make_response("Invalid query argument: 'days'", 400)
        

    if resp is None:
        assert days_raw

        try:
            days = int(days_raw)
        except Exception as e:
            # tb = traceback.format_exc()

            resp = make_response(f"Error with query argument 'days': {e}", 400)
    
    if resp is None:
        data = model.forecast_biowaste(days)

        resp = make_response(jsonify(data), 200)
    
    return resp

@app.route('/data/occupancy')
def forecast_occupancy():
    resp = None

    # Request checking
    days_raw = request.args.get('days')
    if days_raw is None:
        resp = make_response("Invalid query argument: 'days'", 400)
        

    if resp is None:
        assert days_raw

        try:
            days = int(days_raw)
        except Exception as e:
            # tb = traceback.format_exc()

            resp = make_response(f"Error with query argument 'days': {e}", 400)
    
    if resp is None:
        data = model.forecast_occupancy(days)

        resp = make_response(jsonify(data), 200)
    
    return resp



# def biowaste_data():
#     """URL for GET requests of data of biowaste.
#     Returns:
#         JSON: Json Object containing data of biowaste of restaurants. 
# """
#     data =  {'Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)': {
#             '600 Chemicum': [4.453375211733444, 4.453375211733444, 4.453375211733444, 4.453375211733444, 4.453375211733444], 
#             '610 Physicum': [0.11468519322622667, 0.11468519322622667, 0.11468519322622667, 0.11468519322622667, 0.11468519322622667], 
#             '620 Exactum': [3.145200495577108, 3.145200495577108, 3.145200495577108, 3.145200495577108, 3.145200495577108]}, 
#         'Biojäte kahvi. porot (kg) per Kuitti kpl (kg)': {
#             '600 Chemicum': [0.8754721154077725, 0.8754721154077725, 0.8754721154077725, 0.8754721154077725, 0.8754721154077725], 
#             '610 Physicum': [4.252458665954107, 4.252458665954107, 4.252458665954107, 4.252458665954107, 4.252458665954107], 
#             '620 Exactum': [0.8081991367366513, 0.8081991367366513, 0.8081991367366513, 0.8081991367366513, 0.8081991367366513]}, 
#         'Keittiön biojäte (ruoanvalmistus) (kg) per Kuitti kpl (kg)': {
#             '600 Chemicum': [4.887071575939053, 4.887071575939053, 4.887071575939053, 4.887071575939053, 4.887071575939053], 
#             '610 Physicum': [3.1150867597448144, 3.1150867597448144, 3.1150867597448144, 3.1150867597448144, 3.1150867597448144], 
#             '620 Exactum': [4.033277469892359, 4.033277469892359, 4.033277469892359, 4.033277469892359, 4.033277469892359]}, 
#         'Salin biojäte (jämät) (kg) per Kuitti kpl (kg)': {
#             '600 Chemicum': [0.6979051434167958, 0.6979051434167958, 0.6979051434167958, 0.6979051434167958, 0.6979051434167958], 
#             '610 Physicum': [0.06210928888740439, 0.06210928888740439, 0.06210928888740439, 0.06210928888740439, 0.06210928888740439], 
#             '620 Exactum': [0.24476953000106577, 0.24476953000106577, 0.24476953000106577, 0.24476953000106577, 0.24476953000106577]}}
# # def biowaste_data():
# #     data = model.predict_waste_by_week()
# #     print('data biowaste: ', data, flush=True)
#     data_customer = data[
#         "Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)"
#         ]["600 Chemicum"]
#     data_customer = [
#         {'Chemicum': data[
#             "Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)"
#             ]["600 Chemicum"]},
#         {'Exactum': data[
#             'Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)'
#             ]["620 Exactum"]},
#         {'Physicum': data[
#             'Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)'
#             ]["610 Physicum"]}
#     ]
#     data_coffee = [
#         {'Chemicum': data[
#             "Biojäte kahvi. porot (kg) per Kuitti kpl (kg)"
#             ]["600 Chemicum"]},
#         {'Exactum': data[
#             'Biojäte kahvi. porot (kg) per Kuitti kpl (kg)'
#             ]["620 Exactum"]},
#         {'Physicum': data[
#             'Biojäte kahvi. porot (kg) per Kuitti kpl (kg)'
#             ]["610 Physicum"]}
#     ]
#     data_kitchen = [
#         {'Chemicum': data[
#             "Keittiön biojäte (ruoanvalmistus) (kg) per Kuitti kpl (kg)"
#             ]["600 Chemicum"]},
#         {'Exactum': data[
#             'Keittiön biojäte (ruoanvalmistus) (kg) per Kuitti kpl (kg)'
#             ]["620 Exactum"]},
#         {'Physicum': data[
#             'Keittiön biojäte (ruoanvalmistus) (kg) per Kuitti kpl (kg)'
#             ]["610 Physicum"]}
#     ]
#     data_dining = [
#         {'Chemicum': data[
#             "Salin biojäte (jämät) (kg) per Kuitti kpl (kg)"
#             ]["600 Chemicum"]},
#         {'Exactum': data[
#             'Salin biojäte (jämät) (kg) per Kuitti kpl (kg)'
#             ]["620 Exactum"]},
#         {'Physicum': data[
#             'Salin biojäte (jämät) (kg) per Kuitti kpl (kg)'
#             ]["610 Physicum"]}
#     ]
#     return jsonify({
#         'customerBiowaste': data_customer, 
#         'coffeeBiowaste': data_coffee, 
#         'kitchenBiowaste': data_kitchen, 
#         'hallBiowaste': data_dining
#     })

"""URL for GET - requests to get data of division of sold lunches.
    Returns:
        JSON: Json object containing data of sold lunches by food categories / restaurant.
"""
@app.route('/data/menus')
def hardcoded_menu_data():
    df = pd.read_csv("src/data/basic_mvp_data/Sold lunches.csv", sep=";")

    df['Date'] = pd.to_datetime(df['Date'], format="%d.%m.%Y")
    df = df.set_index('Date')

    Chemicum_all = df[df["Restaurant"] == "600 Chemicum"]
    Chem_Q123 = [ len(Chemicum_all.loc['2023-01-01':'2023-03-29'][Chemicum_all.loc['2023-01-01':'2023-03-29']["Food Category"] == "Kala"]),
               len(Chemicum_all.loc['2023-01-01':'2023-03-29'][Chemicum_all.loc['2023-01-01':'2023-03-29']["Food Category"] == "Kana"]),
               len(Chemicum_all.loc['2023-01-01':'2023-03-29'][Chemicum_all.loc['2023-01-01':'2023-03-29']["Food Category"] == "Liha"]),
               len(Chemicum_all.loc['2023-01-01':'2023-03-29'][Chemicum_all.loc['2023-01-01':'2023-03-29']["Food Category"] == "Vegaani"])
    ]
    Chem_Q223 = [ len(Chemicum_all.loc['2023-04-01':'2023-06-30'][Chemicum_all.loc['2023-04-01':'2023-06-30']["Food Category"] == "Kala"]),
               len(Chemicum_all.loc['2023-04-01':'2023-06-30'][Chemicum_all.loc['2023-04-01':'2023-06-30']["Food Category"] == "Kana"]),
               len(Chemicum_all.loc['2023-04-01':'2023-06-30'][Chemicum_all.loc['2023-04-01':'2023-06-30']["Food Category"] == "Liha"]),
               len(Chemicum_all.loc['2023-04-01':'2023-06-30'][Chemicum_all.loc['2023-04-01':'2023-06-30']["Food Category"] == "Vegaani"])
    ]
    Chem_Q323 = [ len(Chemicum_all.loc['2023-07-01':'2023-09-30'][Chemicum_all.loc['2023-07-01':'2023-09-30']["Food Category"] == "Kala"]),
               len(Chemicum_all.loc['2023-07-01':'2023-09-30'][Chemicum_all.loc['2023-07-01':'2023-09-30']["Food Category"] == "Kana"]),
               len(Chemicum_all.loc['2023-07-01':'2023-09-30'][Chemicum_all.loc['2023-07-01':'2023-09-30']["Food Category"] == "Liha"]),
               len(Chemicum_all.loc['2023-07-01':'2023-09-30'][Chemicum_all.loc['2023-07-01':'2023-09-30']["Food Category"] == "Vegaani"])
    ]
    Chem_Q423 = [ len(Chemicum_all.loc['2023-10-01':'2023-12-31'][Chemicum_all.loc['2023-10-01':'2023-12-31']["Food Category"] == "Kala"]),
               len(Chemicum_all.loc['2023-10-01':'2023-12-31'][Chemicum_all.loc['2023-10-01':'2023-12-31']["Food Category"] == "Kana"]),
               len(Chemicum_all.loc['2023-10-01':'2023-12-31'][Chemicum_all.loc['2023-10-01':'2023-12-31']["Food Category"] == "Liha"]),
               len(Chemicum_all.loc['2023-10-01':'2023-12-31'][Chemicum_all.loc['2023-10-01':'2023-12-31']["Food Category"] == "Vegaani"])
    ]

    Exactum_all = df[df["Restaurant"] == "620 Exactum"]
    Exa_Q123 = [ len(Exactum_all.loc['2023-01-01':'2023-03-29'][Exactum_all.loc['2023-01-01':'2023-03-29']["Food Category"] == "Kala"]),
               len(Exactum_all.loc['2023-01-01':'2023-03-29'][Exactum_all.loc['2023-01-01':'2023-03-29']["Food Category"] == "Kana"]),
               len(Exactum_all.loc['2023-01-01':'2023-03-29'][Exactum_all.loc['2023-01-01':'2023-03-29']["Food Category"] == "Liha"]),
               len(Exactum_all.loc['2023-01-01':'2023-03-29'][Exactum_all.loc['2023-01-01':'2023-03-29']["Food Category"] == "Vegaani"])
    ]
    Exa_Q223 = [ len(Exactum_all.loc['2023-04-01':'2023-06-30'][Exactum_all.loc['2023-04-01':'2023-06-30']["Food Category"] == "Kala"]),
               len(Exactum_all.loc['2023-04-01':'2023-06-30'][Exactum_all.loc['2023-04-01':'2023-06-30']["Food Category"] == "Kana"]),
               len(Exactum_all.loc['2023-04-01':'2023-06-30'][Exactum_all.loc['2023-04-01':'2023-06-30']["Food Category"] == "Liha"]),
               len(Exactum_all.loc['2023-04-01':'2023-06-30'][Exactum_all.loc['2023-04-01':'2023-06-30']["Food Category"] == "Vegaani"])
    ]
    Exa_Q323 = [ len(Exactum_all.loc['2023-07-01':'2023-09-30'][Exactum_all.loc['2023-07-01':'2023-09-30']["Food Category"] == "Kala"]),
               len(Exactum_all.loc['2023-07-01':'2023-09-30'][Exactum_all.loc['2023-07-01':'2023-09-30']["Food Category"] == "Kana"]),
               len(Exactum_all.loc['2023-07-01':'2023-09-30'][Exactum_all.loc['2023-07-01':'2023-09-30']["Food Category"] == "Liha"]),
               len(Exactum_all.loc['2023-07-01':'2023-09-30'][Exactum_all.loc['2023-07-01':'2023-09-30']["Food Category"] == "Vegaani"])
    ]
    Exa_Q423 = [ len(Exactum_all.loc['2023-10-01':'2023-12-31'][Exactum_all.loc['2023-10-01':'2023-12-31']["Food Category"] == "Kala"]),
               len(Exactum_all.loc['2023-10-01':'2023-12-31'][Exactum_all.loc['2023-10-01':'2023-12-31']["Food Category"] == "Kana"]),
               len(Exactum_all.loc['2023-10-01':'2023-12-31'][Exactum_all.loc['2023-10-01':'2023-12-31']["Food Category"] == "Liha"]),
               len(Exactum_all.loc['2023-10-01':'2023-12-31'][Exactum_all.loc['2023-10-01':'2023-12-31']["Food Category"] == "Vegaani"])
    ]

    Physicum_all = df[df["Restaurant"] == "610 Physicum"]
    Phy_Q123 = [ len(Physicum_all.loc['2023-01-01':'2023-03-29'][Physicum_all.loc['2023-01-01':'2023-03-29']["Food Category"] == "Kala"]),
               len(Physicum_all.loc['2023-01-01':'2023-03-29'][Physicum_all.loc['2023-01-01':'2023-03-29']["Food Category"] == "Kana"]),
               len(Physicum_all.loc['2023-01-01':'2023-03-29'][Physicum_all.loc['2023-01-01':'2023-03-29']["Food Category"] == "Liha"]),
               len(Physicum_all.loc['2023-01-01':'2023-03-29'][Physicum_all.loc['2023-01-01':'2023-03-29']["Food Category"] == "Vegaani"])
    ]
    Phy_Q223 = [ len(Physicum_all.loc['2023-04-01':'2023-06-30'][Physicum_all.loc['2023-04-01':'2023-06-30']["Food Category"] == "Kala"]),
               len(Physicum_all.loc['2023-04-01':'2023-06-30'][Physicum_all.loc['2023-04-01':'2023-06-30']["Food Category"] == "Kana"]),
               len(Physicum_all.loc['2023-04-01':'2023-06-30'][Physicum_all.loc['2023-04-01':'2023-06-30']["Food Category"] == "Liha"]),
               len(Physicum_all.loc['2023-04-01':'2023-06-30'][Physicum_all.loc['2023-04-01':'2023-06-30']["Food Category"] == "Vegaani"])
    ]
    Phy_Q323 = [ len(Physicum_all.loc['2023-07-01':'2023-09-30'][Physicum_all.loc['2023-07-01':'2023-09-30']["Food Category"] == "Kala"]),
               len(Physicum_all.loc['2023-07-01':'2023-09-30'][Physicum_all.loc['2023-07-01':'2023-09-30']["Food Category"] == "Kana"]),
               len(Physicum_all.loc['2023-07-01':'2023-09-30'][Physicum_all.loc['2023-07-01':'2023-09-30']["Food Category"] == "Liha"]),
               len(Physicum_all.loc['2023-07-01':'2023-09-30'][Physicum_all.loc['2023-07-01':'2023-09-30']["Food Category"] == "Vegaani"])
    ]
    Phy_Q423 = [ len(Physicum_all.loc['2023-10-01':'2023-12-31'][Physicum_all.loc['2023-10-01':'2023-12-31']["Food Category"] == "Kala"]),
               len(Physicum_all.loc['2023-10-01':'2023-12-31'][Physicum_all.loc['2023-10-01':'2023-12-31']["Food Category"] == "Kana"]),
               len(Physicum_all.loc['2023-10-01':'2023-12-31'][Physicum_all.loc['2023-10-01':'2023-12-31']["Food Category"] == "Liha"]),
               len(Physicum_all.loc['2023-10-01':'2023-12-31'][Physicum_all.loc['2023-10-01':'2023-12-31']["Food Category"] == "Vegaani"])
    ]

    All_Q123 = [ len(df.loc['2023-01-01':'2023-03-29'][df.loc['2023-01-01':'2023-03-29']["Food Category"] == "Kala"]),
               len(df.loc['2023-01-01':'2023-03-29'][df.loc['2023-01-01':'2023-03-29']["Food Category"] == "Kana"]),
               len(df.loc['2023-01-01':'2023-03-29'][df.loc['2023-01-01':'2023-03-29']["Food Category"] == "Liha"]),
               len(df.loc['2023-01-01':'2023-03-29'][df.loc['2023-01-01':'2023-03-29']["Food Category"] == "Vegaani"])
    ]
    All_Q223 = [ len(df.loc['2023-04-01':'2023-06-30'][df.loc['2023-04-01':'2023-06-30']["Food Category"] == "Kala"]),
               len(df.loc['2023-04-01':'2023-06-30'][df.loc['2023-04-01':'2023-06-30']["Food Category"] == "Kana"]),
               len(df.loc['2023-04-01':'2023-06-30'][df.loc['2023-04-01':'2023-06-30']["Food Category"] == "Liha"]),
               len(df.loc['2023-04-01':'2023-06-30'][df.loc['2023-04-01':'2023-06-30']["Food Category"] == "Vegaani"])
    ]
    All_Q323 = [ len(df.loc['2023-07-01':'2023-09-30'][df.loc['2023-07-01':'2023-09-30']["Food Category"] == "Kala"]),
               len(df.loc['2023-07-01':'2023-09-30'][df.loc['2023-07-01':'2023-09-30']["Food Category"] == "Kana"]),
               len(df.loc['2023-07-01':'2023-09-30'][df.loc['2023-07-01':'2023-09-30']["Food Category"] == "Liha"]),
               len(df.loc['2023-07-01':'2023-09-30'][df.loc['2023-07-01':'2023-09-30']["Food Category"] == "Vegaani"])
    ]
    All_Q423 = [ len(df.loc['2023-10-01':'2023-12-31'][df.loc['2023-10-01':'2023-12-31']["Food Category"] == "Kala"]),
               len(df.loc['2023-10-01':'2023-12-31'][df.loc['2023-10-01':'2023-12-31']["Food Category"] == "Kana"]),
               len(df.loc['2023-10-01':'2023-12-31'][df.loc['2023-10-01':'2023-12-31']["Food Category"] == "Liha"]),
               len(df.loc['2023-10-01':'2023-12-31'][df.loc['2023-10-01':'2023-12-31']["Food Category"] == "Vegaani"])
    ]


    return jsonify({ 'Chemicum': { 
                        'Q123' : Chem_Q123,
                        'Q223': Chem_Q223,
                        'Q323': Chem_Q323,
                        'Q423' : Chem_Q423 },
                    'Exactum': {
                        'Q123': Exa_Q123,
                        'Q223': Exa_Q223,
                        'Q323': Exa_Q323,
                        'Q423': Exa_Q423,
                    },
                    'Physicum': {
                        'Q123': Phy_Q123,
                        'Q223': Phy_Q223,
                        'Q323': Phy_Q323,
                        'Q423': Phy_Q423,
                    },
                    'Total': {
                        'Q123': All_Q123,
                        'Q223': All_Q223,
                        'Q323': All_Q323,
                        'Q423': All_Q423,
                    }                    
                })

