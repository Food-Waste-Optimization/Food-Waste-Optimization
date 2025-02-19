from datetime import datetime

import pandas as pd
from flask import Blueprint, make_response, render_template, request
from pandas._libs.tslibs.parsing import DateParseError

from src.services import db, model_service
from src.utils.meals import get_meal_data

blueprint = Blueprint("fwo", __name__)
model = model_service.ModelService()

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
def forecast_receipt():
    resp = None

    # Parse necessary arguments and check
    restaurant = request.args.get("restaurant", "")
    if restaurant == "" or restaurant.lower() not in [
        "chemicum",
        "physicum",
        "exactum",
        "viikuna",
    ]:
        resp = make_response("Invalid query argument: 'restaurant'", 400)

    date = request.args.get("date", "")
    if date == "":
        resp = make_response("Invalid query argument: 'date'", 400)

    meal_ids_raw = request.args.get("meal_ids", "")
    if meal_ids_raw == "":
        resp = make_response("Invalid query argument: 'meal_ids'", 400)

    if resp is None:
        meal_ids = list(map(int, meal_ids_raw.split(",")))
        assert len(meal_ids) > 0

        match restaurant.lower():
            case "chemicum":
                restaurant = "che"
            case "exactum":
                restaurant = "exa"
            case "physicum":
                restaurant = "phy"
            case "viikuna":
                restaurant = "vik"

        meals = pd.DataFrame(
            {
                "index": 0,
                "meal_id": meal_ids,
                "restaurant": restaurant,
                "date": pd.to_datetime(date),
            }
        )

        # Predict pcs per meal
        df = model.forecast_pos(meals)
        if df is None:
            resp = make_response(f"meal id not valid: {meal_ids_raw}", 400)
        else:
            # Fetch info of CO2, waste and pcs of whole
            co2 = db.fetch_co2_with_ids(meal_ids=meal_ids)
            biowaste = db.fetch_waste_with_ids(meal_ids=meal_ids)
            pcs_whole = int(
                db.fetch_pos_whole(restaurant=restaurant, date=date)["pcs_whole"]
            )

            df = df.merge(co2, on="meal_id", how="left").merge(
                biowaste, on="meal_id", how="left"
            )
            df["co2"] = df["co2"].fillna(0.4)
            df["waste"] = df["waste"].fillna(0.01)

            out = {"meals": df.to_dict(orient="records"), "whole": pcs_whole}

            resp = make_response(out, 200)
            resp.headers.set("Content-Type", "application/json")

    return resp


@blueprint.route("/visualize")
def visualize():
    resp = None

    restaurant = request.args.get("restaurant", None)
    if (
        restaurant is None
        or not isinstance(restaurant, str)
        or restaurant.lower() not in ["chemicum", "physicum", "exactum", "viikuna"]
    ):
        resp = make_response("Invalid query argument: 'restaurant'", 400)

    if resp is None:
        assert isinstance(restaurant, str)
        meal_data = get_meal_data(restaurant, URL_YLVA_API, datetime.today())

        assert len(meal_data["meals"]) > 0

        # Predict
        meal_info = model.get_meals_prediction(meal_data)

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
    restaurant = request.args.get("restaurant", "")
    if restaurant == "" or restaurant.lower() not in [
        "chemicum",
        "physicum",
        "exactum",
        "viikuna",
    ]:
        resp = make_response("Invalid query argument: 'restaurant'", 400)

    date = request.args.get("date", "")
    if date == "":
        resp = make_response("Invalid query argument: 'date'", 400)

    try:
        assert date
        pd.to_datetime(date)
    except DateParseError:
        resp = make_response("Invalid query argument: 'date'", 400)

    num_rows = request.args.get("num_rows", -1)
    if num_rows == -1:
        resp = make_response("Invalid query argument: 'num_rows'", 400)

    num_weeks = request.args.get("num_weeks", -1)
    if num_weeks == -1:
        resp = make_response("Invalid query argument: 'num_weeks'", 400)

    if resp is None:
        num_weeks = int(num_weeks)
        num_rows = int(num_rows)

        match restaurant.lower():
            case "chemicum":
                restaurant = "che"
            case "exactum":
                restaurant = "exa"
            case "physicum":
                restaurant = "phy"
            case "viikuna":
                restaurant = "vik"

        payload = {}
        for i in range(num_weeks):
            if i == 0:
                date_from = pd.to_datetime(date)
            else:
                date_from = date_from + pd.Timedelta(weeks=1)
            date_to = date_from + pd.Timedelta(days=5)

            # Fetch necessary data
            menus = db.fetch_menu(
                "menu",
                date_from=date_from,
                date_to=date_to,
                restaurant=restaurant,
                num_rows=num_rows,
            )

            # Make up output
            buff = []
            if len(menus) > 0:
                menus["date"] = pd.to_datetime(menus["date"]).dt.strftime("%Y-%m-%d")
                for rank in menus["rank"].unique():
                    df = menus[menus["rank"] == rank]
                    buff.append(df[["date", "meal_ids"]].to_dict(orient="records"))

            payload[f"week_{i + 1}"] = buff

        resp = make_response(payload, 200)
        resp.headers.set("Content-Type", "application/json")

    return resp


@blueprint.route("/meal_info")
def get_meal_info():
    resp = None

    # Parse necessary arguments and check
    restaurant = request.args.get("restaurant", None)
    if (
        restaurant is None
        or not isinstance(restaurant, str)
        or restaurant.lower() not in ["chemicum", "physicum", "exactum", "viikuna"]
    ):
        resp = make_response("Invalid query argument: 'restaurant'", 400)

    schoolyear = request.args.get("schoolyear", "24-25")

    if resp is None:
        assert isinstance(restaurant, str)

        match restaurant.lower():
            case "chemicum":
                restaurant = "che"
            case "exactum":
                restaurant = "exa"
            case "physicum":
                restaurant = "phy"
            case "viikuna":
                restaurant = "vik"

        # Fetch necessary data
        meals = db.fetch_meal_info_with_restaurant(
            restaurant=restaurant, schoolyear=schoolyear
        )

        # Make up output
        buff = meals.to_dict(orient="records")

        resp = make_response(buff, 200)
        resp.headers.set("Content-Type", "application/json")

    return resp
