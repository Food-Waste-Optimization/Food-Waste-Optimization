from pathlib import Path


class Paths:
    DIR_PROCESSED = Path("processed")
    DIR_RAW = Path("../src/data/basic_mvp_data")

    ##############################################################
    # Processed fact table
    ##############################################################
    @staticmethod
    def fact(name: str = "fact.xlsx"):
        return Paths.DIR_PROCESSED / name

    ##############################################################
    # Processed fact table
    ##############################################################
    @staticmethod
    def dim_lucnhes(name: str = "dim_lunches.xlsx"):
        return Paths.DIR_PROCESSED / name

    @staticmethod
    def dim_biowaste(name: str = "dim_biowaste.xlsx"):
        return Paths.DIR_PROCESSED / name

    ##############################################################
    # Raw data
    ##############################################################
    @staticmethod
    def raw_Sold_lunches(name: str = "Sold lunches.csv"):
        return Paths.DIR_RAW / name

    @staticmethod
    def raw_Biowaste(name: str = "Biowaste.csv"):
        return Paths.DIR_RAW / name

    @staticmethod
    def raw_occupancy(name: str = "supersight.xlsx"):
        return Paths.DIR_RAW / name
