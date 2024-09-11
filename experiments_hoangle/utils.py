from pathlib import Path


class Paths:
    DIR_PROCESSED = Path("processed")
    DIR_RAW = Path("../src/data/basic_mvp_data")
    DIR_RESOURCES = Path("processed/res")

    ##############################################################
    # Processed fact table
    ##############################################################
    @staticmethod
    def fact(name: str = "fact.xlsx"):
        return Paths.DIR_PROCESSED / name

    ##############################################################
    # Processed dim tables
    ##############################################################
    @staticmethod
    def dim_lucnhes(name: str = "dim_lunches.xlsx"):
        return Paths.DIR_PROCESSED / name

    @staticmethod
    def dim_biowaste(name: str = "dim_biowaste.xlsx"):
        return Paths.DIR_PROCESSED / name

    ##############################################################
    # Resources
    ##############################################################
    @staticmethod
    def res_dish2embd(name: str = "map_dish2embd.npy"):
        return Paths.DIR_RESOURCES / name

    @staticmethod
    def res_cat2embd(name: str = "map_cat2embd.npy"):
        return Paths.DIR_RESOURCES / name

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
