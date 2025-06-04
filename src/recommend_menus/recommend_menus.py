# NOTE: HoangLe [Jun-04]:
# This file has identical content with notebook `recommend_menus.ipynb`. This file is purposed as running
# the recommended code automatically for multiple weeks


import argparse
import json
import random
import sys
import time
import uuid
from itertools import combinations, product
from pathlib import Path

import pandas as pd
import polars as pl
from loguru import logger
from pandas import DataFrame

from src.forecaster import ModelService

NUM_VEGAN_PER_DAY = 2
NUM_MEALS_PER_DAY = 3
MAX_MEAL_OCCURENCES = 2
NUM_FISH_PER_WEEK = 2

NUM_DAY_LEVEL_MENUS = 1_000_000
NUM_WEEK_LEVEL_MENUS = 1000
NUM_MENUS_FINAL = 20

THETA_CO2 = 0.5
THETA_WASTE = 0.04
THETA_KELA = 2
THETA_GLUTEN = 1

ALPHA_POS = 2
ALPHA_CO2 = 1
ALPHA_WASTE = 1
ALPHA_KELA = 2
ALPHA_GLUTEN = 2

s_gluten = "gluten_free"
s_kela = "kela"
path_dir_menus = Path("data/processed/planned_menu")


def craft_day_level_menu(meals_by_day: dict, restaurant: int, weekday: int, n_max: int = 10_000_000) -> list:
    assert restaurant in meals_by_day and weekday in meals_by_day[restaurant]
    non_vegan = meals_by_day[restaurant][weekday]["non-vegan"]
    vegan = meals_by_day[restaurant][weekday]["vegan"]

    combos = [[x[0], *x[1]] for x in product(non_vegan, combinations(vegan, NUM_VEGAN_PER_DAY))]

    return combos[:n_max]


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--restaurant", "-r", type=str, dest="restaurant")
    parser.add_argument("--date_start", "-s", type=str, dest="date_start")
    parser.add_argument("--date_end", "-e", type=str, dest="date_end")

    args = parser.parse_args()

    return args


def main():
    model = ModelService()
    args = _parse_args()

    restaurant = args.restaurant
    date_start, date_end = args.date_start, args.date_end

    for date_firstweek in pd.date_range(date_start, date_end, freq="7d"):
        logger.info(f"Craft menu for restaurant: {restaurant} - week: {date_firstweek.date()}")

        seed = time.time()
        random.seed(seed)

        # =================================================
        # Load tables
        # =================================================
        path = "data/processed/dim_meal_types.xlsx"

        dim_meal_types = pl.read_excel(path)

        path = "data/processed/dim_meals.parquet"
        dim_meals = pl.read_parquet(path)
        dim_meals.head()

        path = "data/processed/recommended_meal_list.json"
        with open(path) as file:
            meals_by_day_raw = json.load(file)

        meals_by_day = {}
        for restau, weekdays in meals_by_day_raw.items():
            meals_by_day[int(restau)] = {}
            for weekday, meals in weekdays.items():
                meals_by_day[int(restau)][int(weekday)] = meals

        # =================================================
        # Craft day-level menus
        # =================================================

        combos_mon = craft_day_level_menu(meals_by_day, restaurant, 1)
        combos_tue = craft_day_level_menu(meals_by_day, restaurant, 2)
        combos_wed = craft_day_level_menu(meals_by_day, restaurant, 3)
        combos_thu = craft_day_level_menu(meals_by_day, restaurant, 4)
        combos_fri = craft_day_level_menu(meals_by_day, restaurant, 5)

        # =================================================
        # Craft week-level
        # =================================================
        meal_type_fish = dim_meal_types.filter(pl.col("meal_type_en") == pl.lit("fish"))["meal_type_id"].head().item()

        # Create table containing week menu candidates
        menus_week = pl.DataFrame(
            {
                "1": random.choices(combos_mon, k=NUM_DAY_LEVEL_MENUS),
                "2": random.choices(combos_tue, k=NUM_DAY_LEVEL_MENUS),
                "3": random.choices(combos_wed, k=NUM_DAY_LEVEL_MENUS),
                "4": random.choices(combos_thu, k=NUM_DAY_LEVEL_MENUS),
                "5": random.choices(combos_fri, k=NUM_DAY_LEVEL_MENUS),
                "weeklevel_idx": pl.Series([str(uuid.uuid4()) for _ in range(NUM_DAY_LEVEL_MENUS)]),
            }
        )

        ids_valid_week_menu = (
            menus_week
            .select(
                'weeklevel_idx',
                pl.concat_list(["1", "2", "3", "4", "5"]).alias('meal')
            )
            .explode('meal')


            # For each week menu, find the max occurence of meals in the week menu
            .with_columns(
                pl.len().over('weeklevel_idx', 'meal').alias('count_occurence'),
            )
            .with_columns(
                pl.col('count_occurence').max().over('weeklevel_idx').alias('count_max_occurence')
            )

            # Remove week menu candidates not satisfying (3)
            .filter(pl.col('count_max_occurence') <= MAX_MEAL_OCCURENCES)
            


            # Add meal type info and count no. fish meals of each week menu candidate
            .join(dim_meals.select('id', 'meal_type'), left_on='meal', right_on='id', how='left')
            .with_columns(
                (pl.col('meal_type') == meal_type_fish).cast(pl.Int32).alias('is_fish')
            )
            .with_columns(
                pl.col('is_fish').sum().over('weeklevel_idx').alias('count_fish')
            )

            # Remove week menu candidates not satisfying (1.1)
            .filter(pl.col('count_fish') >= NUM_FISH_PER_WEEK)

            .select('weeklevel_idx')
            .unique()
        )  # fmt: skip

        menus_week = (
            menus_week
            .join(ids_valid_week_menu, on='weeklevel_idx', how='inner')
            .sample(NUM_WEEK_LEVEL_MENUS)

            .melt(
                'weeklevel_idx',
                value_vars=["1", "2", "3", "4", "5"],
                variable_name="weekday",
                value_name="meal"
            )

            .with_columns(pl.col('weekday').cast(pl.Int32))
        )  # fmt: skip

        # =================================================
        # Add meal-specific info and date-specific needed for calculating score
        # =================================================
        weekday2date = pl.DataFrame(
            {"weekday": [1, 2, 3, 4, 5], "date": pl.Series(pd.date_range(date_firstweek, periods=5)).dt.date()}
        )

        last_date = weekday2date["date"].max().strftime(r"%Y-%m-%d")
        out = model.forecast_pos_restaurant(restaurant, last_date)
        assert isinstance(out, DataFrame)
        pos_restaurant = (
            pl.from_dataframe(out)
            .select(
                pl.col('date').dt.date(),
                pl.col('forecasted').alias('whole_pos')
            )
        )  # fmt: skip
        out = model.forecast_waste_restaurant(restaurant, last_date)
        assert isinstance(out, DataFrame)
        waste_restaurant = (
            pl
            .from_dataframe(out)
            .select(
                pl.col('date').dt.date(),
                pl.col('forecasted').alias('whole_waste')
            )
        )  # fmt: skip

        menus_week = (
            menus_week
            .explode('meal')

            
            .join(weekday2date, on='weekday')
            .join(dim_meals.select('id', 'meal_type'), left_on='meal', right_on='id', how='left')
            .with_columns(pl.col('date').dt.strftime(r"%Y-%m-%d").alias('date_str'))

            # Forecast POS for each meal
            .with_columns(
                pl.struct('meal', 'date_str', 'meal_type')
                .map_elements(
                    lambda r: model.forecast_pos_per_meal(restaurant, r['meal'], r['date_str'], r['meal_type']),
                    return_dtype=pl.Float32
                ).alias('pos')
            )
            .drop('date_str')

            # Add forecasted restaurant's waste and pos
            .join(pos_restaurant, on='date', how='left')
            .join(waste_restaurant, on='date', how='left')


            # Add CO2, gluten-free and kela for each meal
            .join(
                dim_meals.select(
                    'id', 'co2',
                    pl.col('attributes').list.contains(s_gluten).alias('is_gluten').cast(pl.Int32),
                    pl.col('attributes').list.contains(s_kela).alias('is_kela').cast(pl.Int32),
                ),
                left_on='meal', right_on='id', how='left'
            )
        )  # fmt: skip

        # =================================================
        # Calculate fitness value
        # =================================================
        menus_week = (
            menus_week

            # Calculate score for each date
            .group_by('weeklevel_idx', 'weekday')
            .agg(
                pl.concat_list(pl.struct('meal', 'pos')).flatten().alias('meals_planned'),

                pl.col('pos').sum().alias('sum_pos'),
                (pl.col('pos') * pl.col('co2')).sum().alias('sum_co2_pos'),
                pl.col('is_gluten').sum().alias('sum_gluten'),
                pl.col('is_kela').sum().alias('sum_kela'),

                pl.col('whole_pos').first(),
                pl.col('whole_waste').first(),
            )

            .with_columns(
                (
                    ALPHA_POS * (pl.col('sum_pos') / pl.col('whole_pos') - 1).abs()
                    + ALPHA_CO2 * (pl.col('sum_co2_pos') / pl.col('sum_pos') / THETA_CO2)
                    + ALPHA_WASTE * (pl.col('whole_waste') / pl.col('sum_pos') / THETA_WASTE)
                    + ALPHA_GLUTEN * (1 - pl.col('sum_gluten') / THETA_GLUTEN).clip(0)
                    + ALPHA_KELA * (1 - pl.col('sum_kela') / THETA_GLUTEN).clip(0)
                ).alias('score_day')
            )

            # Calculate score for entire week
            .with_columns(
                pl.col('score_day').sum().over('weeklevel_idx').alias('score_week')
            )
            .with_columns(
                pl.col('score_week').rank('dense', descending=False).over(None).alias('rank')
            )
            .filter(pl.col('rank') <= NUM_MENUS_FINAL)
            .sort('rank')


            # Keep columns as data model
            .join(weekday2date, on='weekday', how='left')
            .select(
                pl.concat_str(
                    [
                        pl.col('weeklevel_idx'),
                        pl.col('date').dt.strftime(r"%Y-%m-%d"), 
                        pl.lit(restaurant)
                    ],
                    separator='|'
                ).alias('id'),
                'weeklevel_idx',
                'date',
                'whole_waste',
                'whole_pos',
                'score_week',
                'meals_planned'
            )
        )  # fmt: skip

        dim_meals_planned = (
            menus_week
            .select(pl.col('id').alias('menu_id'), 'meals_planned')
            .explode('meals_planned')
            .unnest('meals_planned')
        )  # fmt: skip

        # =================================================
        # Save
        # =================================================
        date = date_firstweek.strftime(r"%Y-%m-%d")
        path = path_dir_menus / str(restaurant) / f"menus_{date}.xlsx"
        path.parent.mkdir(exist_ok=True, parents=True)
        menus_week.write_excel(path)

        path = path_dir_menus / str(restaurant) / f"dim_meals_planned_{date}.xlsx"
        dim_meals_planned.write_excel(path)


if __name__ == "__main__":
    sys.exit(main())
