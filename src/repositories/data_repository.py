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
        hourly_customer = pd.read_excel(io="/data/tuntidata2.xlsx", index_col=0)

        # Filter data for the Exactum restaurant
        hourly_customer_exactum = hourly_customer[hourly_customer["Ravintola"] == "620 Exactum"]

        # Aggregate receipt counts by date for Exactum
        receipts_by_date_exactum = hourly_customer_exactum.groupby("Date").sum()["Kuitti kpl"]

        # Merge multiple Excel sheets into one DataFrame
        customer_data = self.merge_multiple_excel_sheets("data/kumpula_data.xlsx")
        
        # Get people flow data by date
        supersight_data = self.get_people_flow_by_date("data/supersight-raw-data.csv")

        # Merge receipts, customer data, and people flow data
        data = pd.merge(receipts_by_date_exactum, customer_data, on="Date", how="inner")
        data = pd.merge(data, supersight_data, on="Date", how="inner")

        # Calculate next day's waste and fill NaN values with 0
        data = self.get_next_day_waste(data).fillna(value=0)

        # Add a column for the weekday
        data['Weekday'] = data.index.dayofweek

        # Filter out rows where the total is less than or equal to 0
        data = data[data["Yhteensä"] > 0]

        # Print the processed data
        print(data)

        return data

    def get_next_day_waste(self, data):
        """
        Add a column for the next day's waste based on the 'Yhteensä' column.

        Args:
            data (pandas.DataFrame): The DataFrame to modify.

        Returns:
            pandas.DataFrame: The modified DataFrame with the next day's waste.
        """
        data['Huomisen Jäte'] = data['Yhteensä'].shift(-1)
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

    def merge_multiple_excel_sheets(self, filename):
        """
        Combine data from multiple Excel sheets into one DataFrame.

        Args:
            filename (str): Path to the Excel file.

        Returns:
            pandas.DataFrame: The combined data from multiple sheets.
        """
        # Read multiple sheets from Excel file
        excel_data = pd.read_excel(io=filename, sheet_name=None, skiprows=1, index_col=0)

        # Extract and process data for Exactum
        sold_meals_exactum = excel_data["Myydyt lounaat"]["620 Exactum"][1:]
        cols_for_exactum = excel_data["Myytyjen lounaiden suhde"].columns[-14:]
        dist_sold_meals_exactum = excel_data["Myytyjen lounaiden suhde"][cols_for_exactum][1:]

        cols_for_exactum = excel_data["Biojäte"].columns[10:-5]
        biowaste_exactum = excel_data["Biojäte"][cols_for_exactum]

        # Set up a new header for biowaste data
        new_header = biowaste_exactum.iloc[0]
        biowaste_exactum = biowaste_exactum[2:]
        biowaste_exactum.columns = new_header

        # Merge all data based on index (date)
        combined_data = pd.merge(sold_meals_exactum, dist_sold_meals_exactum, left_index=True, right_index=True, how="outer")
        combined_data = pd.merge(combined_data, biowaste_exactum, left_index=True, right_index=True, how="outer")

        # Insert Date column and set it as the index
        np.insert(combined_data.columns.values, 0, "Date")
        combined_data["Date"] = pd.to_datetime(combined_data.index.values, dayfirst=True)
        combined_data = combined_data.set_index(keys="Date")

        return combined_data

data_repository = DataRepository()
