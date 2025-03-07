from urllib.request import urlopen
import json
from datetime import datetime


def get_restaurant_menus(restaurant_name: str, data) -> list | None:
    """
    Function for parsing the key-value pairs matching the given
    restaurant name from JSON data.

    Args:
        restaurant_name (str): A string containing the restaurant's name
        data (JSON): Data in JSON format.

    Returns:
        list|None: The matching key-value pairs as a list.
    """
    result = []
    for item in data:
        if item["title"].lower() == restaurant_name.lower():
            for menu in item["menuData"]["menus"]:
                result.append(menu)
    if result:
        return result
    return None


def get_meal_data(restaurant: str, url: str, date: datetime) -> dict | None:
    """
    Function for getting meal data for a given restaurant name
    from JSON data located at given address.
    Date defaults to current day.

    Args:
        restaurant (str): A string containing the restaurant's name
        url (str): The url for restaurant data
        date (datetime): Optional, a date in datetime format, defaulting to today
    Returns:
        dict|None: A dictionary of the format
                   {
                    "meals": A list containing meal names for the day
                    "restaurant": The abbreviated restaurant name
                    "date": The date as a str
                   }
    """
    response = urlopen(url)

    data_json = json.loads(response.read())

    menus = get_restaurant_menus(restaurant, data_json)

    meals = []

    if menus is None:
        print("Restaurant not found")
        return None

    for item in menus:
        if item["data"] and item["date"].split()[1] == date.strftime("%d.%m."):
            for meal in item["data"]:
                # Ignore announcements in meal data. "RAVINTOLA SULJETTU" means restaurant closed,
                # "Lakkouhka" is about a strike.
                # Makeasti and Lisuke stand for Dessert and Side dish respectively.
                if meal["name"] not in ["Lakkouhka",
                                        "RAVINTOLA SULJETTU"] and meal["price"]["name"] not in [
                    "Makeasti",
                    "Lisuke",
                ]:
                    meals.append(meal["name"])

    match restaurant.lower():
        case "chemicum":
            restaurant = "che"
        case "exactum":
            restaurant = "exa"
        case "physicum":
            restaurant = "phy"
        case "viikuna":
            restaurant = "vik"

    meals_data = {
        "meals": meals,
        "restaurant": restaurant,
        "date": date.strftime("%Y-%m-%d"),
    }

    return meals_data
