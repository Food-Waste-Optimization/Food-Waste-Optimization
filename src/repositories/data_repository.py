import pandas as pd
import numpy as np


class DataRepository:
    """Class to handle connection to data streams and manage data operations."""

    def get_df_from_stationary_data(self):
        """
        Retrieve and process stationary data from the 'data' folder, specifically 
        for the Exactum restaurant. Useful for testing and basic MVP.

        - Reads customer data and receipt counts.
        - Merges customer data, receipt counts, and people flow data.
        - Calculates next day's waste and filters the data.

        Returns:
            pandas.DataFrame: The processed data.
        """
        # Read hourly customer data from Excel
        hourly_customer = pd.read_excel(
            io="src/data/basic_mvp_data/tuntidata2.xlsx", index_col=0)

        # Filter data for the Exactum restaurant
        hourly_customer_exactum = hourly_customer[hourly_customer["Ravintola"]
                                                  == "620 Exactum"]

        # Aggregate receipt counts by date for Exactum
        receipts_by_date_exactum = hourly_customer_exactum.groupby("Date").sum()[
            "Kuitti kpl"]

        customer_data = pd.read_csv(
            "src/data/basic_mvp_data/kumpula_lounaat_kat.csv", sep=";", skiprows=2)
        customer_data = customer_data.drop([0, 1])
        customer_data = customer_data.drop(
            columns=customer_data.columns[1:-14], axis="columns")
        customer_data = customer_data.drop(
            columns=customer_data.columns[-1], axis="columns")

        customer_data["Date"] = pd.to_datetime(customer_data["Unnamed: 0"])
        customer_data = customer_data.drop(
            columns=customer_data.columns[0], axis="columns")

        # Get people flow data by date
        #supersight_data = self.get_people_flow_by_date("src/data/basic_mvp_data/supersight-raw-data.csv")

        # Merge receipts, customer data, and people flow data
        data = pd.merge(receipts_by_date_exactum,
                        customer_data, on="Date", how="inner")

        data.set_index("Date", inplace=True)
        #data = pd.merge(data, supersight_data, on="Date", how="inner")

        # Calculate next day's waste and fill NaN values with 0
        data = data.fillna(value=0)

        # Add a column for the weekday
        data['Weekday'] = data.index.dayofweek

        # Change percentage strings to a float between 0 and 1
        for column in data:
            if column[0] == "%":
                data[column] = data[column].str.replace("%", '')
                data[column] = data[column].str.replace(" ", '')
                data[column] = data[column].str.replace(",", '.').astype(float)
                data[column] = data[column] / 100

        self.get_menu_items()

        return data

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

        df = pd.read_excel(
            io="src/data/basic_mvp_data/tuntidata2.xlsx", index_col=0)

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

    def roll_means(self, value: int = 5):
        df = self.get_df_from_stationary_data()
        #df.set_index('Date', inplace=True)
        rolling_means = df.rolling(window=value).mean()
        rolling_means['Next day sold meals'] = df['Total.2'].shift(-1)
        rolling_means['Weekday'] = df['Weekday']
        rolling_means.dropna(inplace=True)
        return rolling_means.apply(pd.to_numeric, errors='coerce')

    def get_avg_meals_waste_ratio(self):
        """Computes the average ratio of meals sold
        to biowaste produced by one customer.

        !!! Requires "Biowaste.csv" file !!!

        Returns:
            float: ratio meals_sold:waste_produced per 1 customer
        """
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


data_repository = DataRepository()

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
    print(data_repository.get_avg_meals_waste_ratio())
