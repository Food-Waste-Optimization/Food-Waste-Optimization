from datetime import datetime

import pandas as pd
from flask import Blueprint, make_response, render_template, request
from loguru import logger

from src.services import db
from src.services.model_service import model
from src.utils import meals

blueprint = Blueprint("fwo", __name__)

DEFAULT_CO2 = 0.4
DEFAULT_WASTE = 0.01
URL_YLVA_API = "https://unicafe.fi/wp-json/swiss/v1/restaurants?wpml_language=en"

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
@blueprint.route("/forecast/pos")
def forecast():
    resp = None

    # Parse necessary arguments and check
    restaurant = request.args.get("restaurant", None)
    if restaurant is None or not isinstance(restaurant, str):
        resp = make_response("Invalid query argument: 'restaurant'", 400)
    restaurant_info = db.fetch_restaurant_info(restaurant=restaurant)
    if restaurant_info is None:
        resp = make_response(f"Specified restaurant not found in database: {restaurant}", 400)

    date = request.args.get("date", "")
    if date == "":
        resp = make_response("Invalid query argument: 'date'", 400)

    meal_ids_raw = request.args.get("meal_ids", "")
    if meal_ids_raw == "":
        resp = make_response("Invalid query argument: 'meal_ids'", 400)

    if resp is None:
        meal_ids = list(map(int, meal_ids_raw.split(",")))
        assert len(meal_ids) > 0

        restaurant_id = restaurant_info["restaurant_id"]
        restaurant_short = restaurant_info["restaurant_short"]

        meals = pd.DataFrame(
            {
                "index": 0,
                "meal_id": meal_ids,
                "restaurant": restaurant_id,
                "date": pd.to_datetime(date),
            }
        )

        # Forecast whole-restaurant waste
        df = model.forecast_waste_restaurant(restaurant_id, date)
        assert df is not None
        waste_whole_res = df["forecasted"]

        # Forecast whole-restaurant POS
        df = model.forecast_pos_restaurant(restaurant_id, date)
        assert df is not None
        pos_whole_res = df[df["date"] == date]["forecasted"].item()

        # Forecast per-meal POS
        meals = db.fetch_meal_info_with_ids(meal_ids=meal_ids)
        meals["pcs_pred"] = meals.apply(
            lambda r: model.forecast_pos_per_meal(restaurant_id, r["id"], date, r["meal_type"]),
            axis=1,
        )

        # Post-process
        meals["date"] = date
        meals["index"] = 0
        meals.rename(columns={"id": "meal_id"}, inplace=True)
        meals["restaurant"] = restaurant_short
        meals["waste"] = waste_whole_res / meals["pcs_pred"].sum()
        meals["co2"] = meals["co2"].fillna(DEFAULT_CO2)
        meals.drop(columns=["names", "restaurants", "attributes"], inplace=True)

        out = {"meals": meals.to_dict(orient="records"), "whole": pos_whole_res}

        resp = make_response(out, 200)
        resp.headers.set("Content-Type", "application/json")

    return resp


@blueprint.route("/visualize")
def visualize():
    resp = None

    restaurant = request.args.get("restaurant", None)
    if restaurant is None or not isinstance(restaurant, str):
        resp = make_response("Invalid query argument: 'restaurant'", 400)
    restaurant_info = db.fetch_restaurant_info(restaurant=restaurant)
    if restaurant_info is None:
        resp = make_response(f"Specified restaurant not found in database: {restaurant}", 400)

    if resp is None:
        assert isinstance(restaurant, str)
        meal_data = meals.get_meal_data(restaurant, URL_YLVA_API, datetime.today())
        assert meal_data

        # Predict
        if len(meal_data["meals"]) > 0:
            meal_info = model.get_meals_prediction(restaurant_info["restaurant_id"], meal_data)
        else:
            meal_info = []

        restaurant = meal_data["restaurant"]
        date = meal_data["date"]
        out = {"meals": meal_info, "restaurant": restaurant, "date": date}
        resp = make_response(out, 200)
        resp.headers.set("Content-Type", "application/json")

    return resp


# == APIs for Recommendation ===================================================================================================================
@blueprint.route("/recommendation")
def recommend_menu():
    resp = None

    # Parse necessary arguments and check
    restaurant = request.args.get("restaurant", None)
    if restaurant is None or not isinstance(restaurant, str):
        resp = make_response("Invalid query argument: 'restaurant'", 400)
    restaurant_info = db.fetch_restaurant_info(restaurant=restaurant)
    if restaurant_info is None:
        resp = make_response(f"Specified restaurant not found in database: {restaurant}", 400)

    date = request.args.get("date", None)
    if date is None:
        resp = make_response("Invalid query argument: 'date'", 400)

    try:
        assert date
        datetime.strptime(date, "%Y-%M-%d")
    except ValueError:
        logger.error(f"Invalid query argument: 'date': {date}")

        resp = make_response(f"Invalid query argument: 'date': {date}", 400)

    num_rows = request.args.get("num_rows", -1)
    if num_rows == -1:
        resp = make_response("Invalid query argument: 'num_rows'", 400)

    num_weeks = request.args.get("num_weeks", -1)
    if num_weeks == -1:
        resp = make_response("Invalid query argument: 'num_weeks'", 400)

    if resp is None:
        num_weeks = int(num_weeks)
        num_rows = int(num_rows)

        restaurant_id = restaurant_info["restaurant_id"]

        payload = {}
        for i in range(num_weeks):
            if i == 0:
                date_from = pd.to_datetime(date)
            else:
                date_from = date_from + pd.Timedelta(weeks=1)

            # Fetch necessary data
            menus = db.fetch_menu(
                date_from=date_from,
                restaurant=restaurant_id,
                num_rows=num_rows,
            )

            # Make up output
            buff = []
            if len(menus) > 0:
                for weeklevel_idx in menus["weeklevel_idx"].unique():
                    df = menus[menus["weeklevel_idx"] == weeklevel_idx].drop(columns=["weeklevel_idx", "score"])

                    buff.append(df.to_dict(orient="records"))

            payload[f"week_{i + 1}"] = buff

        resp = make_response(payload, 200)
        resp.headers.set("Content-Type", "application/json")

    return resp


@blueprint.route("/meal_info")
def get_meal_info():
    resp = None

    # Parse necessary arguments and check
    restaurant = request.args.get("restaurant", None)
    if restaurant is None or not isinstance(restaurant, str):
        resp = make_response("Invalid query argument: 'restaurant'", 400)
    restaurant_info = db.fetch_restaurant_info(restaurant=restaurant)
    if restaurant_info is None:
        resp = make_response(f"Specified restaurant not found in database: {restaurant}", 400)

    schoolyear = request.args.get("schoolyear", "24-25")

    if resp is None:
        restaurant_id = restaurant_info["restaurant_id"]

        # Fetch necessary data
        meals = db.fetch_meal_info_with_restaurant(restaurant=restaurant_id, schoolyear=schoolyear)

        # Make up output
        buff = meals.to_dict(orient="records")

        resp = make_response(buff, 200)
        resp.headers.set("Content-Type", "application/json")

    return resp
