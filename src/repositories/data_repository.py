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
        hourly_customer = pd.read_excel(io="src/data/basic_mvp_data/tuntidata2.xlsx", index_col=0)

        # Filter data for the Exactum restaurant
        hourly_customer_exactum = hourly_customer[hourly_customer["Ravintola"] == "620 Exactum"]

        # Aggregate receipt counts by date for Exactum
        receipts_by_date_exactum = hourly_customer_exactum.groupby("Date").sum()["Kuitti kpl"]

        customer_data = pd.read_csv("src/data/basic_mvp_data/kumpula_lounaat_kat.csv", sep=";", skiprows=2)
        customer_data = customer_data.drop([0,1])
        customer_data = customer_data.drop(columns=customer_data.columns[1:-14], axis="columns")
        customer_data = customer_data.drop(columns=customer_data.columns[-1], axis="columns")

        customer_data["Date"]  = pd.to_datetime(customer_data["Unnamed: 0"])
        customer_data = customer_data.drop(columns=customer_data.columns[0], axis="columns")

        # Get people flow data by date
        #supersight_data = self.get_people_flow_by_date("src/data/basic_mvp_data/supersight-raw-data.csv")

        # Merge receipts, customer data, and people flow data
        data = pd.merge(receipts_by_date_exactum, customer_data, on="Date", how="inner")

        data.set_index("Date", inplace=True)
        #data = pd.merge(data, supersight_data, on="Date", how="inner")

        # Calculate next day's waste and fill NaN values with 0
        data = data.fillna(value=0)

        # Add a column for the weekday
        data['Weekday'] = data.index.dayofweek

        #Change percentage strings to a float between 0 and 1
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
        data.loc[data['phoneName'] == 'S113', ['countIn', 'countOut']] = data.loc[data['phoneName'] == 'S113', ['countOut', 'countIn']].values

        # Convert date column to datetime and set it as the index
        data["Date"] = pd.to_datetime(data["dateCreated"])
        data.set_index("Date", inplace=True)
        
        # Calculate the daily sum difference of people entering and leaving
        daily_sum_diff = data.resample('D').sum()['countIn'] - data.resample('D').sum()['countOut']
        daily_sum_diff.name = "People flow diff"

        # Remove timezone information
        return daily_sum_diff.tz_convert(None)


    def get_menu_items(self):

        # Save data file as excel and gather relevant data into dataframe    
        csv_path = "src/data/basic_mvp_data/kumpula_menu.csv"
        excel_path = "src/data/basic_mvp_data/kumpula_menu.xlsx"
        read_file_product = pd.read_csv(csv_path, sep=";")
        read_file_product.to_excel(excel_path, index=None, header=False)
        menu_data = pd.read_excel("src/data/basic_mvp_data/kumpula_menu.xlsx")
        menu_data = menu_data.drop([0, 1], axis=0)
        menu_data = menu_data.drop(columns=menu_data.columns[0:-3])
        menu_data.drop(axis='columns', columns='Total.2', inplace=True)
        menu_data.dropna(axis=0, how='all', inplace=True)
        menu_data.rename(columns={menu_data.columns[0]: 'Menu item'}, inplace=True)
        menu_data.rename(columns={menu_data.columns[1]: 'Meals sold'}, inplace=True)
        menu_data["Date"] = np.nan

        # Save dates that are among menu item data into their own column
        menu_data.reset_index()
        for indexx, row in menu_data.iterrows():
            if len(row['Menu item']) == 10 and row['Menu item'][0] == "2":
                menu_data.loc[indexx, "Date"] = row['Menu item']
            else:
                menu_data.loc[indexx, "Date"] = menu_data.loc[indexx-1, "Date"]


        #print(menu_data)

        return menu_data
    

    def roll_means(self, value:int = 5):
        df = self.get_df_from_stationary_data()
        #df.set_index('Date', inplace=True)
        rolling_means = df.rolling(window=value).mean()
        rolling_means['Next day sold meals'] = df['Total.2'].shift(-1)
        rolling_means['Weekday'] = df['Weekday']
        rolling_means.dropna(inplace=True)
        return rolling_means.apply(pd.to_numeric, errors='coerce')

data_repository = DataRepository()

if __name__ == "__main__":
    data_repository = DataRepository()
    data = data_repository.get_df_from_stationary_data()
    print(data)
