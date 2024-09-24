import traceback

from flask import Blueprint, jsonify, make_response, render_template, request

from src.services import model_service

# from ..app.app import app

blueprint = Blueprint("fwo", __name__)


model = model_service.ModelService()


# == APIs for Others ===================================================================================================================

"""Route for testing database connection. 
    Returns:
        Can be used to return test data
"""


@blueprint.route("/")
@blueprint.route("/fwowebserver")
def initial_view():
    resp = make_response(render_template("index.html"))
    resp.headers["Accept-Ranges"] = "none"

    return resp


# == APIs for Forecast ===================================================================================================================
@blueprint.route("/forecast/receipts")
def forecast_receipt():
    resp = None

    # Request checking
    days_raw = request.args.get("days")
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


@blueprint.route("/forecast/biowaste")
def forecast_biowaste():
    resp = None

    # Request checking
    days_raw = request.args.get("days")
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


@blueprint.route("/forecast/occupancy")
def forecast_occupancy():
    resp = None

    # Request checking
    days_raw = request.args.get("days")
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


@blueprint.route("/forecast/meal")
def forecast_meal():
    resp = None

    # Request checking
    days_raw = request.args.get("days")
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
        data = model.forecast_sold_meals(days)

        resp = make_response(jsonify(data), 200)

    return resp


@blueprint.route("/forecast/biowaste_from_meals")
@blueprint.route("/forecast/biowaste_from_meals")
def biowaste_from_meals():
    resp = None

    # Request checking
    restaurant = request.args.get("restaurant", None)
    if (
        restaurant is None
        or not isinstance(restaurant, str)
        or restaurant not in ["Chemicum", "Physicum", "Exactum"]
    ):
        resp = make_response("Invalid query argument: 'restaurant'", 400)

    return_type = request.args.get("return_type", None)
    if (
        return_type is None
        or not isinstance(return_type, str)
        or return_type not in ["image", "numeric"]
    ):
        resp = make_response("Invalid query argument: 'return_type'", 400)

    num_meals = {
        "num_fish": 0,
        "num_chicken": 0,
        "num_vegetarian": 0,
        "num_meat": 0,
        "num_vegan": 0,
    }
    for meal_type in num_meals.keys():
        num = request.args.get(meal_type)
        if meal_type is None:
            resp = make_response(f"Invalid query argument: '{meal_type}'", 400)

            break

        num_meals[meal_type] = float(num)

    if resp is None:
        try:
            assert restaurant
            assert return_type
            buf = model.forecast_biowaste_with_meal(
                restaurant=restaurant, **num_meals, return_type=return_type
            )

            resp = make_response(buf, 200)
            if isinstance(buf, dict):
                resp.headers.set("Content-Type", "application/json")
            else:
                resp.headers.set("Content-Type", "image/png")
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)

            resp = make_response(f"Error: {e}", 500)

    return resp


@blueprint.route("/forecast/co2_from_meals")
def co2_from_meals():
    resp = None

    # Request checking
    restaurant = request.args.get("restaurant", None)
    if (
        restaurant is None
        or not isinstance(restaurant, str)
        or restaurant not in ["Chemicum", "Physicum", "Exactum"]
    ):
        resp = make_response("Invalid query argument: 'restaurant'", 400)

    num_meals = {
        "num_fish": 0,
        "num_chicken": 0,
        "num_vegetarian": 0,
        "num_meat": 0,
        "num_vegan": 0,
    }
    for meal_type in num_meals.keys():
        num = request.args.get(meal_type)
        if meal_type is None:
            resp = make_response(f"Invalid query argument: '{meal_type}'", 400)

            break

        num_meals[meal_type] = float(num)

    if resp is None:
        try:
            assert restaurant
            buf = model.forecast_co2_with_meal(restaurant=restaurant, **num_meals)

            resp = make_response(buf, 200)
            resp.headers.set("Content-Type", "application/json")
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)

            resp = make_response(f"Error: {e}", 500)

    return resp
