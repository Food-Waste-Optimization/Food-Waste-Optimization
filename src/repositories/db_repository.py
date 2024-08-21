from ..app.db import db, engine
import pandas as pd
import numpy as np


class DatabaseRepository:
    """Class to insert data into database. Can be
    used to initialize with data and add data to 
    existing database.
    """
    def __init__(self):
        self.database_connection = engine

    def test_connection(self):
        pass

# RESTAURANT DATA

    def insert_biowaste(self, filepath="src/data/basic_mvp_data/Biowaste.csv"):
        """Function to insert biowaste data from csv file to database.
        Requires csv file which is modified to allow datapoints to be float: repl "," -> "."
        Will append new data to old, if old exists.

        Args:
            filepath (str, optional): filepath of biowaste data. Defaults to 
            "src/data/basic_mvp_data/Biowaste.csv".
        """

        # try to load biowaste file and create DateTime object to it
        try:
            df = pd.read_csv(filepath, sep=";", decimal=(","))
            df.index = pd.to_datetime(df.pop("Date"), format="%d.%m.%Y")
            df = df.rename(mapper={"Ravintola": "Restaurant", 
                                   "Asiakasbiojäte, tiski (kg)": "biowaste_customer", 
                                   "Biojäte kahvi, porot (kg)": "biowaste_coffee",
                                   "Keittiön biojäte (ruoanvalmistus) (kg)": "biowaste_kitchen",
                                   "Salin biojäte (jämät) (kg)": "biowaste_hall"},
                                    axis="columns")
            df.index.name = "date"
        except Exception as err: # pylint: disable=W0718
            print("Error in trying to load biowaste file or creating DateTime object from it:", err)

        # try to process data str -> float and insert into database
        try:
            df.iloc[:,-4:] = df.iloc[:,-4:].astype(float)
            df["restaurant_id"] = self.insert_restaurants(df.pop("Restaurant"))
            df.to_sql(name="biowaste", con=self.database_connection, if_exists="append")
        except Exception as err: # pylint: disable=W0718
            print(
                "Error in inserting biowaste data into database. "
                "The file might be the wrong format. Try replacing ',' with '.':",
                err
            )

    def insert_sold_meals(self, filepath="src/data/basic_mvp_data/Sold lunches.csv"):
        """Function to insert sold lunches data from csv file to database.
        Requires a specific csv file. Will append new data if old is found.

        Args:
            filepath (str, optional): filepath of sold lunches data.
            Defaults to "src/data/basic_mvp_data/Sold lunches.csv".
        """

        # create a dataframe from the file and create DateTime object from timestamps
        try:
            df = pd.read_csv(filepath, sep=";", dtype=str)
            date_time_str = df['Date'] + ' ' + df['Receipt time']
            df['datetime'] = pd.to_datetime(date_time_str, format="%d.%m.%Y %H:%M")
            # df['date'] = pd.to_datetime(df['Date'], format="%d.%m.%Y")
            # df['time'] = pd.to_datetime(df['Receipt time'], format="%H:%M")
            df = df.drop(columns=["Date", "Receipt time"])
        except Exception as err: # pylint: disable=W0718
            print(
                "Error in trying to create a datetime object from dataframe, "
                "or importing data from file:", err
            )
        # split dataframe into separate Series objects for specific processing, names become ids
        try:
            df["restaurant_id"] = self.insert_restaurants(df.pop("Restaurant"))

        except Exception as err:
            print("Error in inserting restaurant data into database:", err)

        try:
            # category can be dropped, not needed in database. Get category_id for the dishes.
            category_id = self.insert_food_categories(df.pop("Food Category"))

        except Exception as err:
            print("Error in inserting category data into database:", err)


        dish = df.pop("Dish")
        hiilijalanjalki = self.comma_nums_to_float(df.pop("Hiilijalanjälki"))
        pcs = self.comma_nums_to_float(df["pcs"])
        co2 = hiilijalanjalki / pcs
        df_dish = pd.DataFrame({"name" : dish, "carbon_footprint" : co2.round(2), "category_id" : category_id})
        
        try:
            df["dish_id"] = self.insert_dishes(df_dish)
 
        except Exception as err: # pylint: disable=W0718
            print("Error in inserting dishes into database:", err)

        # insert remaining dataframe into database
        df["amount"] = df.pop("pcs").str.replace(" ", "0")

        # Eliminate the existing sold_lunches data from the new data
        df_db = self.get_sold_meals_data()
        # times = df_db.pop("time").astype(str)
        # df_db['time'] = pd.to_datetime(times, format="%H:%M:%S")
        df = pd.concat([df, df_db]).drop_duplicates(subset=['datetime', 'restaurant_id', 'dish_id'], keep=False)

        try:
            df.to_sql(name="sold_lunches", con=self.database_connection, if_exists="append", index=False)
        except Exception as err: # pylint: disable=W0718
            print(
                "Error in inserting sold lunches into database."
                "The file might be the wrong format.", err
            )

    def insert_restaurants(self, restaurants: pd.Series):
        """Function to insert restaurants to database. If exists,
        skip, if new, append to old. Will create ids from restaurant names
        and return them. Restaurant id is 600, 610 etc.

        Args:
            restaurants (pd.Series): restaurants, e.g. 600 Chemicum

        Returns:
            restaurant ids (pd.Series): ids as int, e.g. 600
        """
        try:
            split_values = np.char.split(restaurants.values.astype(str), " ")
            values = [(item[0], item[1]) for item in split_values]
            ids = np.array([value[0] for value in split_values]).astype(int)
        except Exception as err: # pylint: disable=W0718
            print("Processing restaurant data caused an error:", err)

        try:
            # Make a dataframe of restaurant data
            df = pd.DataFrame(values, columns=["id", "name"])
            df.set_index("id", inplace=True)
            df = df.drop_duplicates(keep='last')

            # Eliminate the existing restaurant data from the new data
            df2 = self.get_restaurant_data()
            df = pd.concat([df, df2]).drop_duplicates(keep=False)

            # Add new restaurant data to database
            df.to_sql("restaurants", con=self.database_connection, if_exists="append")
        except Exception as err: # pylint: disable=W0718
            print("Error in inserting restaurant data into database:", err)

        return ids

    def insert_food_categories(self, categories: pd.Series):
        """Function to insert food categories to database.
        After inserting into database, ids are fetched from 
        database and returned.

        Args:
            categories (pd.Series): categories of food, e.g. meat, fish

        Returns:
            ids : ids to replace the name representation of the category in a pd.Series
        """

        # Eliminate the existing category data from the new data
        sr1 = categories.drop_duplicates()
        sr1 = sr1.rename("name")
        sr2 = self.get_categories_data()['name']
        sr = pd.concat([sr1, sr2]).drop_duplicates(keep=False)

        # Add the new category data to database
        try :
            sr.to_sql("categories", con=self.database_connection, if_exists="append", index=False)
        except Exception as err: # pylint: disable=W0718
            print("Error in inserting food category data into database:", err)

        # Return category ids as a pd.Series
        categories.name = "name"
        table = self.get_categories_data()
        ids = pd.merge(categories, table, 'left', 'name')
        return ids.pop('id')

    def insert_dishes(self, dish_data: pd.DataFrame):
        """Function to insert dishes and their CO2 emissions (e.g. Nakkikastike 0.56) to database.
        After inserting into database, ids are fetched from 
        database and returned.

        Args:
            categories (pd.Series): names of dishes, e.g. Nakkikastike CO2Emissions

        Returns:
            ids : ids to replace the name representation of the dish name in a pd.Series
        """
        # dish_data["Dish"] = dish_data["Dish"].astype(str)

        # Eliminate the existing dish data from the new data
        df1 = dish_data.drop_duplicates(keep='last')
        df2 = self.get_dish_data().set_index("id")
        df = pd.concat([df1, df2]).drop_duplicates(subset=['name', 'carbon_footprint', 'category_id'], keep=False)

        # Add the dish data to database
        try :
            df.to_sql("dishes", con=self.database_connection, if_exists="append", index=False)
        except Exception as err: # pylint: disable=W0718
            print("Error in inserting dish data into database:", err)
        
        # Return dish ids as a pd.Series
        table = self.get_dish_data()
        ids = pd.merge(dish_data, table, how='left', on=['name', 'carbon_footprint', 'category_id'])
        return ids.pop("id")

    def comma_nums_to_float(self, series: pd.Series):
        """For a pandas Series object that has values like
        0,7, turn the values into 0.7 as a float.

        Args:
            series (pd.Series): values to change

        Returns:
            pd.Series: changed values as float
        """
        series = series.str.replace(" ", "0")
        return series.str.replace(",", ".").astype(float).round(2)
    
    def get_values_from_ids(self, table: str, value_name: str, id_list: list):
        """Function to fetch data corresponding to its id from
        the database. 

        !!!Check the correct table name and value_name from schema!!!

        Args:
            table (str): name of table
            value_name (str): name of value to fetch, e.g. "name"
            id_list (list): list of ids, e.g. [1, 2, 3, 4, 5]

        Returns:
            list: values corresponding to the ids
        """
        # make sure ids are a list
        if type(id_list) != list:
            id_list = id_list.tolist()

        placeholders = ', '.join(['%s'] * len(id_list))

        query = f"SELECT id, {value_name} FROM {table} WHERE id IN ({placeholders})"

        result = pd.read_sql_query(sql=query, con=self.database_connection, params=tuple(id_list))
        
        result_dict = dict(zip(result['id'], result[value_name]))
        
        ordered_values = [result_dict.get(id, None) for id in id_list]
        
        return ordered_values

    def get_sold_meals_data(self):
        return pd.read_sql_table("sold_lunches", con=self.database_connection)

    def get_biowaste_data(self):
        return pd.read_sql_table("biowaste", con=self.database_connection)

    def get_occupancy_data(self):
        # for people flow data
        pass

    def get_receipt_data(self):
        return pd.read_sql_table("customers_per_hour", con=self.database_connection)

    def get_categories_data(self):
        return pd.read_sql_table("categories", con=self.database_connection)

    def get_restaurant_data(self):
        df = pd.read_sql_table("restaurants", con=self.database_connection)
        df.set_index("id", inplace=True)
        return df

    def get_dish_data(self):
        return pd.read_sql_table("dishes", con=self.database_connection)

# RESULT DATA

    def insert_nlp_encoding(self, data : pd.DataFrame):
        """Function to insert NLP lemmas and encoding to database for later use.

        Args:
            data (pd.DataFrame): DataFrame with 'lemma' (str) as an index and 'encoding' (integer[])
        """

        try:
            data.to_sql("nlp_encoding", con=self.database_connection, if_exists='replace')
        except Exception as err:
            print("Error in inserting NLP encoding into database:", err)

    def get_nlp_encoding(self, lemma : str):
        """Function to get an encoding for a lemma.

            Args: lemma (str): a lemma used in NLP

            Returns: result: result of SQL query as pd.DataFrame
        """

        sql = f"SELECT encoding FROM nlp_encoding WHERE lemma = '{lemma}'"

        try:
            result = pd.read_sql_query(sql, self.database_connection)
            return result
        except Exception as err:
            print("Error in getting encoding from database:", err)
    def fetch_latest_weekly_prediction(self):
        """Fetch the latest prediction of sold meals
        from the database.
        """
        pass

    def fetch_latest_biowaste_prediction(self):
        """Fetch the latest biowaste prediction
        from the database."""
        pass

    def fetch_latest_occupancy_prediction(self):
        """Fetch the latest prediction of occupancy
        from the database."""
        pass

    def insert_weekly_prediction(self, prediction):
        """Store a prediction of sold meals
        to the database.
        """
        pass

    def insert_biowaste_prediction(self, prediction):
        """Store a prediction of created biowaste
        to the database.
        """
        pass

    def insert_occupancy_prediction(self, prediction):
        """Store a prediction of occupancy
        to the database.
        """
        pass


    

db_repo = DatabaseRepository()

if __name__ == "__main__":
    db_repo = DatabaseRepository()
    db_repo.insert_sold_lunches()
