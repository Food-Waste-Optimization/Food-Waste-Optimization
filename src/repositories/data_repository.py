import pandas as pd
import numpy as np
from .db_repository import db_repo
from ..services.language_processor import language_processor


class DataRepository:
    """Class to handle connection to data streams and manage data operations."""

    def get_model_fit_data(self):
        """
        Retrieve and process sold meals data from the database. 

        - Take in the unprocessed data from the database:
            sold meals data

        - Create a dataframe that has:
            sold meals, weekday, menu items
            as machine understandable way (one hot encoding)

        Returns:
            pandas.DataFrame: The processed data.
        """
        return None
        data = db_repo.get_sold_meals_data()

        if data:
            data = self.process_menu_items(data["Dish"])

        # run language processing for menu items
        # create weekday column
        data["weekday"] = data.index.dayofweek

        print("data repo", data)

        # one hot encoding for menu items using nlp
        data["Dish"] = language_processor.process_learn(data["Dish"])
            

        # group into restaurants, by date?

        return data
    
    def get_model_predict_data(self):
        pass

    def get_people_flow_by_date(self, filename):
        """
        Calculate the daily difference of people entering and leaving based on 
        supersight camera data.

        Args:
            filename (str): Path to the CSV file with supersight data.

        Returns:
            pandas.Series: The daily difference in people flow.
        """
        # Read people flow data from CSV
        data = pd.read_csv(filepath_or_buffer=filename, sep=",")

        # Cameras in Exa/Phy counts are wrong way around for counting people in Exa
        data.loc[data['phoneName'] == 'S113', ['countIn', 'countOut']
                 ] = data.loc[data['phoneName'] == 'S113', ['countOut', 'countIn']].values

        # Convert date column to datetime and set it as the index
        data["Date"] = pd.to_datetime(data["dateCreated"])
        data.set_index("Date", inplace=True)

        # Calculate the daily sum difference of people entering and leaving
        daily_sum_diff = data.resample('D').sum(
        )['countIn'] - data.resample('D').sum()['countOut']
        daily_sum_diff.name = "People flow diff"

        # Remove timezone information
        return daily_sum_diff.tz_convert(None)

    def get_average_occupancy(self):
        """Computes the average occupancy of three restaurants
        in Kumpula. Creates a dictionary that has the restaurant
        as a main key and the day as another. Then, for each day it holds a list
        for the average occupancy for each hour of the day (0-23).

        Currently only works for three restaurants.

        Returns:
            dict: avg occupancy by hour for each rest for each day
        """

        df = db_repo.get_occupancy_data()

        df = df.replace({"600 Chemicum": "Chemicum",
                        "610 Physicum": "Physicum", "620 Exactum": "Exactum"})

        df["weekday"] = df.index.dayofweek

        grouped_df = df.groupby(
            ["Ravintola", "weekday", "Kuitin tunti"]).mean().to_dict()["Kuitti kpl"]

        restaurants = ["Chemicum", "Physicum", "Exactum"]

        occupancy = {
            restaurant: {
                day: [
                    grouped_df.get((restaurant, day, hour), 0)
                    for hour in range(24)
                ]
                for day in range(7)
            }
            for restaurant in restaurants
        }

        return occupancy

    def get_avg_meals_waste_ratio(self):
        """Computes the average ratio of meals sold
        to biowaste produced by one customer.

        !!! Requires "Biowaste.csv" file !!!

        Returns:
            float: ratio meals_sold:waste_produced per 1 customer
        """

        # Should be replaced with call to db_repo
        df = pd.read_csv("src/data/basic_mvp_data/Biowaste.csv", sep=";")
        df.index = pd.to_datetime(df.pop("Date"), format="%d.%m.%Y")

        grouped_biowaste = df.groupby(["Ravintola"]).sum().astype(float)

        df2 = pd.read_excel(io="src/data/basic_mvp_data/tuntidata2.xlsx",
                            index_col=0).groupby(["Ravintola"]).sum().drop(columns="Kuitin tunti")

        data = grouped_biowaste.merge(df2, on=["Ravintola"], how="inner")

        # Compute the ratio
        for column in data.columns.values:
            ratio_column_name = f'{column} per Kuitti kpl (kg)'
            data[ratio_column_name] = data[column] / data['Kuitti kpl']
            data.pop(column)
        data.pop("Kuitti kpl per Kuitti kpl (kg)")

        return data.to_dict()


    def test_db(self):
        if False:
            db_repo.insert_biowaste()
            db_repo.insert_sold_meals()
            print("inserted")

            print("Restaurants:")
            print(db_repo.get_restaurant_data().head())
            print("Biowaste:")
            print(db_repo.get_biowaste_data().head())
            print("Categories:")
            print(db_repo.get_categories_data().head())
            print("Dishes:")
            print(db_repo.get_dish_data().head())
            print("Sold lunches:")
            print(db_repo.get_sold_meals_data().head())

data_repo = DataRepository()

if __name__ == "__main__":
    #from ..app.index import DATABASE_URL, app
    #from flask_sqlalchemy import SQLAlchemy
    #from sqlalchemy import text

    #app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    #db = SQLAlchemy(app)

    #data = data_repository.get_df_from_stationary_data()
    #roll = data_repository.roll_means()

    #rs = db.session.execute(text("SELECT * from test"))
    #result = rs.fetchone()
    # print(result)
    print(data_repo.get_avg_meals_waste_ratio())
