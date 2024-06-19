from sqlalchemy import text
import pandas as pd
import numpy as np


def insert_df_to_db(name: str, df, engine):
    df.to_sql(name=name, con=engine, if_exists='replace')
    return


def lookup_table_from_db(db, name):
    sql = text(f"SELECT * FROM {name};")
    rs = db.session.execute(sql)
    result = rs.fetchall()
    return result

class DatabaseRepository:
    """Class to insert data into database. Can be
    used to initialize with data and add data to 
    existing database.
    """
    def __init__(self, db_connection=None):
        self.database_connection = db_connection

    def insert_biowaste(self, filepath="src/data/basic_mvp_data/Biowaste.csv"):
        """Function to insert biowaste data from csv file to database.
        Requires csv file which is modified to allow datapoints to be float: repl "," -> "."
        Will append new data to old, if old exists.

        Args:
            filepath (str, optional): filepath of biowaste data. Defaults to "src/data/basic_mvp_data/Biowaste.csv".
        """

        # try to load biowaste file and create DateTime object to it
        try:
            df = pd.read_csv(filepath, sep=";")
            df.index = pd.to_datetime(df.pop("Date"), format="%d.%m.%Y")
        except Exception as error:
            print("Error in trying to load biowaste file or creating DateTime object from it:", error)

        # try to process data str -> float and insert into database
        try:
            df.iloc[:,-4:] = df.iloc[:,-4:].astype(float)
            df.to_sql(name="biowaste", con=self.database_connection, if_exists="append")
        except Exception as error:
            print("Error in inserting biowaste data into database. The file might be the wrong format. Try replacing ',' with '.':", error)

    def insert_sold_lunches(self, filepath="src/data/basic_mvp_data/Sold lunches.csv"):
        """Function to insert sold lunches data from csv file to database.
        Requires a specific csv file. Will append new data if old is found.

        Args:
            filepath (str, optional): filepath of sold lunches data. Defaults to "src/data/basic_mvp_data/Sold lunches.csv".
        """
        
        # create a dataframe from the file and create DateTime object from timestamps
        try:
            df = pd.read_csv(filepath, sep=";", low_memory=False)
            df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Receipt time'], format="%d.%m.%Y %H:%M")
            df = df.drop(columns=["Date", "Receipt time", "Unnamed: 6", "Unnamed: 7", "Unnamed: 8"])
        except KeyError as error:
            print("Error in trying to create a datetime object from dataframe:", error)

        # split dataframe into separate Series objects for specific processing, names become ids
        try:
            df["Restaurant"] = self.insert_restaurants(df["Restaurant"])
            df["Dish"] = self.insert_dishes(df["Dish"])

            # category can be dropped, not needed in database
            self.insert_food_categories(df.pop("Food Category"))
        except KeyError as error:
            print("Error in splitting data into separate Series objects:", error)

        # insert remaining dataframe into database
        try:
            print(df)
            #df.to_sql(name="sold_lunches", con=self.database_connection, if_exists="append")
        except KeyError as error:
            print("Error in inserting sold lunches into database. The file might be the wrong format.", error)
    
    def insert_restaurants(self, restaurants: pd.Series):
        """Function to insert restaurants to database. If exists,
        skip, if new, append to old. Will create ids from restaurant names
        and return them. Restaurant id is 600, 610 etc.

        Args:
            restaurants (pd.Series): restaurants, e.g. 600 Chemicum

        Returns:
            restaurant ids (pd.Series): ids as int, e.g. 600
        """
        split_values = np.char.split(restaurants.values.astype(str), " ")
        ids = np.array([value[0] for value in split_values]).astype(int)
        return ids
        
    def insert_food_categories(self, categories: pd.Series):
        pass

    def insert_dishes(self, dishes: pd.Series):
        pass


if __name__ == "__main__":
    db_repo = DatabaseRepository()
    db_repo.insert_sold_lunches()