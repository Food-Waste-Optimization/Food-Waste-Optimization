from urllib.request import urlopen
import json
from datetime import datetime


def get_restaurant_menus(restaurant_name: str, data) -> list:
    result = []
    for item in data:
        if item["title"].lower() == restaurant_name.lower():
            for menu in item["menuData"]["menus"]:
                result.append(menu)
    if result:
        return result
    return None


def get_meal_data(restaurant: str, url: str, date: datetime = datetime.today()) -> dict:
    response = urlopen(url)

    data_json = json.loads(response.read())

    menus = get_restaurant_menus(restaurant, data_json)

    meals = []

    if menus is None:
        print("Restaurant not found")
        return None

    for item in menus:
        if item["data"] and item["date"].split()[1] == date.strftime("%d.%m."):
            for dish in item["data"]:
                # Ignore announcements in meal data. "Lakkouhka" is about a strike.
                # Makeasti and Lisuke stand for Dessert and Side dish respectively.
                if "Lakkouhka" not in dish["name"] and dish["price"]["name"] not in [
                    "Makeasti",
                    "Lisuke",
                ]:
                    meals.append(dish["name"])

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
