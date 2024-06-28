from flask import render_template, jsonify, make_response, request
import pandas as pd

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
@app.route('/data/occupancy')
def hardcoded_occupancy_data():
    # data = {'Chemicum': {
    #         0: [0, 0, 0, 0, 0, 0, 0, 1.0, 1.7575757575757576, 2.5517241379310347, 38.62686567164179, 240.2089552238806, 236.2537313432836, 146.7462686567164, 110.34328358208955, 4.934426229508197, 5.333333333333333, 3.0, 0, 0, 0, 0, 0, 0],
    #         1: [0, 0, 0, 0, 0, 0, 0, 1.0, 2.085714285714286, 2.7719298245614037, 34.957142857142856, 227.5142857142857, 238.21428571428572, 136.0857142857143, 102.58571428571429, 4.73015873015873, 3.4285714285714284, 2.5, 1.0, 0, 0, 0, 0, 0], 
    #         2: [0, 0, 0, 0, 0, 0, 0, 0, 2.28125, 2.564516129032258, 35.405797101449274, 218.46376811594203, 224.47826086956522, 136.52173913043478, 105.18840579710145, 5.360655737704918, 2.0, 4.0, 6.5, 0, 0, 0, 0, 0], 
    #         3: [0, 0, 0, 0, 0, 0, 0, 0, 2.2, 2.732142857142857, 32.98550724637681, 214.0, 218.68115942028984, 139.768115942029, 100.56521739130434, 5.590163934426229, 3.0, 2.6666666666666665, 7.0, 8.0, 0, 0, 0, 0], 
    #         4: [0, 0, 0, 0, 0, 0, 0, 1.0, 2.8529411764705883, 2.8666666666666667, 36.74626865671642, 204.08955223880596, 202.47761194029852, 124.6268656716418, 93.64179104477611, 5.203389830508475, 1.6, 3.6666666666666665, 0, 1.0, 0, 0, 0, 0], 
    #         5: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    #         6: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, 
    #   'Physicum': {
    #         0: [0, 0, 0, 0, 0, 0, 4.0, 4.0, 19.142857142857142, 29.821428571428573, 35.660714285714285, 58.857142857142854, 63.67857142857143, 65.67857142857143, 75.01886792452831, 76.0204081632653, 33.275, 0, 0, 0, 0, 0, 0, 0], 
    #         1: [0, 0, 0, 0, 0, 4.0, 4.166666666666667, 4.555555555555555, 20.17241379310345, 33.275862068965516, 43.13793103448276, 60.741379310344826, 72.72413793103448, 66.86206896551724, 76.18181818181819, 81.12, 33.21951219512195, 0, 0, 0, 0, 0, 0, 0], 
    #         2: [0, 0, 0, 0, 0, 0, 3.230769230769231, 3.8275862068965516, 20.839285714285715, 30.160714285714285, 39.214285714285715, 64.375, 71.6842105263158, 72.2, 82.05660377358491, 78.8695652173913, 31.833333333333332, 0, 0, 0, 0, 0, 0, 0], 
    #         3: [0, 0, 0, 0, 0, 0, 3.5, 4.15625, 21.436363636363637, 29.272727272727273, 39.03636363636364, 58.10909090909091, 67.56363636363636, 71.4, 73.49019607843137, 75.5625, 34.5, 0, 0, 0, 0, 0, 0, 0], 
    #         4: [0, 0, 0, 0, 0, 0, 4.5, 3.423076923076923, 24.134615384615383, 32.17307692307692, 41.34615384615385, 58.03846153846154, 60.509433962264154, 53.58490566037736, 61.714285714285715, 16.21875, 1.2, 0, 0, 0, 0, 0, 0, 0], 
    #         5: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 6: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, 
    #   'Exactum': {
    #             0: [0, 0, 0, 0, 0, 0, 0, 1.0, 1.3333333333333333, 1.25, 1.736842105263158, 143.19565217391303, 113.02173913043478, 65.29787234042553, 5.704545454545454, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    #             1: [0, 0, 0, 0, 0, 0, 4.0, 1.0, 1.5, 1.5555555555555556, 2.3461538461538463, 138.3125, 133.95833333333334, 73.14583333333333, 4.8478260869565215, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    #             2: [0, 0, 0, 0, 0, 0, 0, 1.0, 1.2, 1.5, 2.074074074074074, 141.04444444444445, 133.9111111111111, 71.13333333333334, 4.674418604651163, 0, 1.0, 0, 0, 0, 0, 0, 0, 0], 
    #             3: [0, 0, 0, 0, 0, 0, 0, 1.0, 1.6666666666666667, 1.3076923076923077, 1.8846153846153846, 143.51162790697674, 112.34883720930233, 71.81395348837209, 4.341463414634147, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    #             4: [0, 0, 0, 0, 0, 0, 1.0, 1.0, 1.0, 1.7272727272727273, 2.0, 123.9090909090909, 113.0, 48.56818181818182, 3.9047619047619047, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    #             5: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 6: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}
    # return data

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
        data = model.predict_occupancy(days)

        resp = make_response(jsonify(data), 200)
    
    return resp

# def occupancy_data():
#     data = model.predict_occupancy()
#     print('data occupancy: ', data, flush=True)
#     return data
"""URL for GET requests of data of biowaste.
    Returns:
        JSON: Json Object containing data of biowaste of restaurants. 
"""
@app.route('/data/biowaste')
def hardcoded_biowaste_data():
    data =  {'Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)': {
            '600 Chemicum': [4.453375211733444, 4.453375211733444, 4.453375211733444, 4.453375211733444, 4.453375211733444], 
            '610 Physicum': [0.11468519322622667, 0.11468519322622667, 0.11468519322622667, 0.11468519322622667, 0.11468519322622667], 
            '620 Exactum': [3.145200495577108, 3.145200495577108, 3.145200495577108, 3.145200495577108, 3.145200495577108]}, 
        'Biojäte kahvi. porot (kg) per Kuitti kpl (kg)': {
            '600 Chemicum': [0.8754721154077725, 0.8754721154077725, 0.8754721154077725, 0.8754721154077725, 0.8754721154077725], 
            '610 Physicum': [4.252458665954107, 4.252458665954107, 4.252458665954107, 4.252458665954107, 4.252458665954107], 
            '620 Exactum': [0.8081991367366513, 0.8081991367366513, 0.8081991367366513, 0.8081991367366513, 0.8081991367366513]}, 
        'Keittiön biojäte (ruoanvalmistus) (kg) per Kuitti kpl (kg)': {
            '600 Chemicum': [4.887071575939053, 4.887071575939053, 4.887071575939053, 4.887071575939053, 4.887071575939053], 
            '610 Physicum': [3.1150867597448144, 3.1150867597448144, 3.1150867597448144, 3.1150867597448144, 3.1150867597448144], 
            '620 Exactum': [4.033277469892359, 4.033277469892359, 4.033277469892359, 4.033277469892359, 4.033277469892359]}, 
        'Salin biojäte (jämät) (kg) per Kuitti kpl (kg)': {
            '600 Chemicum': [0.6979051434167958, 0.6979051434167958, 0.6979051434167958, 0.6979051434167958, 0.6979051434167958], 
            '610 Physicum': [0.06210928888740439, 0.06210928888740439, 0.06210928888740439, 0.06210928888740439, 0.06210928888740439], 
            '620 Exactum': [0.24476953000106577, 0.24476953000106577, 0.24476953000106577, 0.24476953000106577, 0.24476953000106577]}}
# def biowaste_data():
#     data = model.predict_waste_by_week()
#     print('data biowaste: ', data, flush=True)
    data_customer = data[
        "Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)"
        ]["600 Chemicum"]
    data_customer = [
        {'Chemicum': data[
            "Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)"
            ]["600 Chemicum"]},
        {'Exactum': data[
            'Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)'
            ]["620 Exactum"]},
        {'Physicum': data[
            'Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)'
            ]["610 Physicum"]}
    ]
    data_coffee = [
        {'Chemicum': data[
            "Biojäte kahvi. porot (kg) per Kuitti kpl (kg)"
            ]["600 Chemicum"]},
        {'Exactum': data[
            'Biojäte kahvi. porot (kg) per Kuitti kpl (kg)'
            ]["620 Exactum"]},
        {'Physicum': data[
            'Biojäte kahvi. porot (kg) per Kuitti kpl (kg)'
            ]["610 Physicum"]}
    ]
    data_kitchen = [
        {'Chemicum': data[
            "Keittiön biojäte (ruoanvalmistus) (kg) per Kuitti kpl (kg)"
            ]["600 Chemicum"]},
        {'Exactum': data[
            'Keittiön biojäte (ruoanvalmistus) (kg) per Kuitti kpl (kg)'
            ]["620 Exactum"]},
        {'Physicum': data[
            'Keittiön biojäte (ruoanvalmistus) (kg) per Kuitti kpl (kg)'
            ]["610 Physicum"]}
    ]
    data_dining = [
        {'Chemicum': data[
            "Salin biojäte (jämät) (kg) per Kuitti kpl (kg)"
            ]["600 Chemicum"]},
        {'Exactum': data[
            'Salin biojäte (jämät) (kg) per Kuitti kpl (kg)'
            ]["620 Exactum"]},
        {'Physicum': data[
            'Salin biojäte (jämät) (kg) per Kuitti kpl (kg)'
            ]["610 Physicum"]}
    ]
    return jsonify({
        'customerBiowaste': data_customer, 
        'coffeeBiowaste': data_coffee, 
        'kitchenBiowaste': data_kitchen, 
        'hallBiowaste': data_dining
    })

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

