from ..services import model_service
from flask import render_template, jsonify, make_response
from ..app.app import app


model = model_service.ModelService()
model.load_model()


@app.route("/dbtest")
def db_conn_test():
    # data = data_repository.DataRepository()
    # df = data.get_df_from_stationary_data()
    # roll = data.roll_means()

    # engine = init_engine(app)

    # dbrepo.insert_df_to_db("dataframe", df, engine)
    # dbrepo.insert_df_to_db("rolleddata",roll, engine)

    # rs = dbrepo.lookup_table_from_db(db, name="dataframe")
    # rs2 = dbrepo.lookup_table_from_db(db, name="rolleddata")
    # return (str(rs), str(rs2))

    value = db_repository.get_test_value()
    return value


@app.route("/")
@app.route("/fwowebserver")
def initial_view():
    resp = make_response(render_template('index.html'))
    resp.headers['Accept-Ranges'] = 'none'

    return resp

@app.route('/api/data')
def get_data_for_wednesday():
    with open('src/data/predicted.txt', mode='r') as file:
        prediction = file.readline()
        return jsonify({'content': prediction })
    
@app.route('/data/occupancy')
def occupancy_data():
    data = data_repository.DataRepository().get_average_occupancy()
    return data

@app.route('/data/biowaste')
def biowaste_data():
    data = model.predict_waste_by_week()
    data_customer = data["Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)"]["600 Chemicum"]
    data_customer = [{'Chemicum': data["Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)"]["600 Chemicum"]},
                        {'Exactum': data['Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)']["620 Exactum"]},
                        {'Physicum': data['Asiakasbiojäte. tiski (kg) per Kuitti kpl (kg)']["610 Physicum"]}
                        ]
    data_coffee = [{'Chemicum': data["Biojäte kahvi. porot (kg) per Kuitti kpl (kg)"]["600 Chemicum"]},
                    {'Exactum': data['Biojäte kahvi. porot (kg) per Kuitti kpl (kg)']["620 Exactum"]},
                    {'Physicum': data['Biojäte kahvi. porot (kg) per Kuitti kpl (kg)']["610 Physicum"]}
                    ]
    data_kitchen = [{'Chemicum': data["Keittiön biojäte (ruoanvalmistus) (kg) per Kuitti kpl (kg)"]["600 Chemicum"]},
                    {'Exactum': data['Keittiön biojäte (ruoanvalmistus) (kg) per Kuitti kpl (kg)']["620 Exactum"]},
                    {'Physicum': data['Keittiön biojäte (ruoanvalmistus) (kg) per Kuitti kpl (kg)']["610 Physicum"]}
                    ]
    data_dining = [{'Chemicum': data["Salin biojäte (jämät) (kg) per Kuitti kpl (kg)"]["600 Chemicum"]},
                    {'Exactum': data['Salin biojäte (jämät) (kg) per Kuitti kpl (kg)']["620 Exactum"]},
                    {'Physicum': data['Salin biojäte (jämät) (kg) per Kuitti kpl (kg)']["610 Physicum"]}
                    ]
    return jsonify({'customerBiowaste': data_customer, 'coffeeBiowaste': data_coffee, 'kitchenBiowaste': data_kitchen, 'hallBiowaste': data_dining})
