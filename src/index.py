from flask import Flask, render_template, jsonify
from routers.data_router import DataRouter
#from src.services.analysis import example_model
import os
from config import set_configuration
from flask_cors import CORS

app = Flask(__name__, static_url_path='',
            static_folder='frontend/dist',
            template_folder='frontend/dist')
CORS(app)

configuration_mode = os.getenv('FLASK_ENV')
app.config.from_object(set_configuration(configuration_mode))

print('Mode: ', app.config["CONFIG_MODE"], flush=True)
print('Key: ', app.config["SECRET_KEY"], flush=True)

app.add_url_rule('/data', view_func=DataRouter().render_view)


@app.route("/")
@app.route("/fwowebserver")
def initial_view():
    return render_template('index.html')

@app.route('/api/data')
def get_data_for_wednesday():
    #prediction = example_model()
    prediction = 130
    return jsonify({'content': prediction })

if __name__ == "__main__":
    app.run(host='0.0.0.0')
