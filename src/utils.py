import holidays
import polars as pl
from polars import DataFrame

PATHS = {
    "dim_meals": "data/processed/phase_4/dim_meals.parquet",
    "pos": [
        "data/raw/pos/Sold lunches.csv",
        "data/raw/pos/Sold lunches Kumpula 6-8 2024.csv",
        "data/raw/pos/Sold lunches Kumpula 9-10 2024.csv",
        "data/raw/pos/Sold lunches Viikuna 2023.csv",
        "data/raw/pos/Sold lunches Viikuna 2024.csv",
    ],
    "embeddings": "data/inter/meal_names_embds.parquet",
}


class Data:
    DATE_START = pl.lit("2023-01-02").str.to_date()
    DATE_END = pl.lit("2024-10-31").str.to_date()

    def __init__(self) -> None:
        self.dim_meals: DataFrame = self._load_meals()
        self.dim_meal_types: DataFrame = self._load_meal_types()
        self.dim_meal_names: DataFrame = self._load_meal_names()
        self.dim_exam: DataFrame = self._load_exam()
        self.dim_holiday: DataFrame = self._load_holiday()
        self.dim_opentime: DataFrame = self._load_opentime()
        self.dim_embds: DataFrame = self._load_embeddings()

        self.pos: DataFrame = self._load_pos()

    def _load_meals(self, name: str = "dim_meals") -> DataFrame:
        dim_meals = pl.read_parquet(PATHS[name])

        return dim_meals

    def _load_meal_types(self) -> DataFrame:
        dim_meal_types = self.dim_meals.select("meal_id", "meal_type")

        return dim_meal_types

    def _load_meal_names(
        self,
    ) -> DataFrame:
        dim_meal_names = (
            self.dim_meals
            .select(
                'meal_id',
                pl.col('aliases').alias('meal')
            )
            .explode('meal')
        )  # fmt: skip

        return dim_meal_names

    def _load_opentime(self) -> DataFrame:
        dim_opentime = (
            pl
            .from_records([
                {'restaurant': 'che', 'time_open': '10:30', 'time_close': '15:00'},
                {'restaurant': 'exa', 'time_open': '11:00', 'time_close': '14:00'},
                {'restaurant': 'phy', 'time_open': '10:00', 'time_close': '15:00'},
                {'restaurant': 'vik', 'time_open': '10:30', 'time_close': '14:00'},
            ])
            .select(
                'restaurant',
                pl.col('time_open').str.to_datetime("%H:%M"),
                pl.col('time_close').str.to_datetime("%H:%M")
            )
            .with_columns(
                ((pl.col('time_close') - pl.col('time_open')).dt.total_minutes() / 60.).alias('working_duration')
            )
        )  # fmt: skip

        return dim_opentime

    def _load_exam(self):
        dim_exam_raw = (
            pl
            .from_records([
                {'date_begin': '2023-03-06', 'date_end': '2023-03-12'},  
                {'date_begin': '2023-05-01', 'date_end': '2023-05-07'},
                {'date_begin': '2023-10-23', 'date_end': '2023-10-29'},
                {'date_begin': '2023-12-18', 'date_end': '2023-12-24'},
                {'date_begin': '2024-03-04', 'date_end': '2024-03-10'},
                {'date_begin': '2024-05-06', 'date_end': '2024-05-12'},
                {'date_begin': '2024-10-21', 'date_end': '2024-10-27'},
            ])
            .with_columns(
                pl.col('date_begin').str.to_date(),
                pl.col('date_end').str.to_date(),
            )
        )  # fmt: skip

        df = (
            pl.DataFrame()

            # Create blank dataframe with date
            .with_columns(
                pl.date_range(Data.DATE_START, Data.DATE_END, '1d').alias('date')
            )
        )  # fmt: skip

        entries_exam = (
            df
            .join(dim_exam_raw, how='cross')
            .filter(
                (pl.col('date') >= pl.col('date_begin'))
                & (pl.col('date') <= pl.col('date_end'))
            )
            .select(
                'date',
                pl.lit(True).alias('is_exam')
            )
        )  # fmt: skip
        dim_exam = (
            df
            .join(entries_exam, on='date', how='left')
            .with_columns(pl.col('is_exam').fill_null(False).cast(pl.Int32))

            # Remove non-business days
            .filter(pl.col('date').dt.weekday() < 6)
        )  # fmt: skip

        return dim_exam

    def _load_holiday(self) -> DataFrame:
        fin_holidays = holidays.Finland(years=[2023, 2024, 2025])
        dim_holiday_raw = pl.from_records([{"date": d, "name_holiday": n} for d, n in fin_holidays.items()])

        dim_holiday = (
            pl.DataFrame()

            # Create blank dataframe with date
            .with_columns(
                pl.date_range(Data.DATE_START, Data.DATE_END, '1d').alias('date')
            )


            # Add dim holiday
            .join(dim_holiday_raw, on='date', how='left')
            .with_columns(pl.col('name_holiday').is_not_null().cast(pl.Int32).alias('is_holiday'))
            .drop('name_holiday')

            # Remove non-business days
            .filter(pl.col('date').dt.weekday() < 6)
        )  # fmt: skip

        return dim_holiday

    def _load_embeddings(self, name: str = "embeddings") -> DataFrame:
        embeddings = pl.read_parquet(PATHS[name])

        return embeddings

    def _load_pos(self, name: str = "pos") -> DataFrame:
        raw = []
        for path in PATHS[name]:
            df = pl.read_csv(path, separator=";", has_header=False, skip_rows=1)
            # df.columns = np.arange(df.shape[1], dtype=str)
            raw.append(df)

        pos = pl.concat(raw)

        # Rename columns
        pos.columns = ["date", "time", "restaurant", "meal_type", "meal", "pcs", "co2"]

        # Convert pcs
        pos = pos.filter((pl.col("pcs").is_not_null()) & (pl.col("pcs") >= 0))

        # Map restaurant name
        names_restaurant = {
            "600 Chemicum": "che",  #'chemicum',
            "610 Physicum": "phy",  #'physicum',
            "620 Exactum": "exa",  #'exactum'
            "570 Viikuna": "vik",
        }
        pos = pos.with_columns(pl.col("restaurant").replace_strict(names_restaurant))

        # Process date
        pos = (
            pos
            .with_columns(
                (pl.col('date') + " " + pl.col('time')).str.to_datetime("%d.%m.%Y %H:%M").alias('datetime')
            )
            .drop('date', 'time')
        )  # fmt: skip

        # Process meal
        pos = (
            pos

            # Remove trailing spaces
            .with_columns(
                pl.col('meal').str.strip_chars(' ')
            )

            
            # Get meal_id
            .join(self.dim_meal_names, on='meal', how='left')

            
            # Remove entries having no `meal_id`
            .filter(pl.col('meal_id').is_not_null())
        )  # fmt: skip

        # Aggregate by date and supplement serving duration per day
        pos = (
            pos
            .group_by('restaurant', pl.col('datetime').dt.date().alias('date'), 'meal_id')
            .agg(
                pl.col('pcs').sum(),
                pl.col('datetime').min().alias('time_start'),
                pl.col('datetime').max().alias('time_end'),
            )
            .with_columns(
                ((pl.col('time_end') - pl.col('time_start')).dt.total_minutes() / 60.).alias('serving_duration')
            )
            .join(
                self.dim_opentime.select('restaurant', 'working_duration'),
                on='restaurant',
                how='left'
            )
            .with_columns(
                (pl.col('serving_duration') / pl.col('working_duration')).alias('serving_percent')
            )
        )  # fmt: skip

        # Remove redundant columns
        pos = pos.drop("time_start", "time_end", "serving_duration", "working_duration")

        # Add meal_type
        pos = (
            pos
            .join(
                self.dim_meals.select('meal_id', 'meal_type'),
                on='meal_id',
                how='left'
            )
        )  # fmt: skip

        # Ignore buffet
        pos = pos.filter(pl.col("meal_type") != pl.lit("buffet"))

        # Remove pos of leftover meals
        pos = (
            pos
            .with_columns(
                pl.col('date').shift(1).over('restaurant', 'meal_id', order_by='date').alias('date_lag'),
                pl.col('pcs').shift(1).over('restaurant', 'meal_id', order_by='date').alias('pcs_lag'),
            )
            .filter(
                (pl.col('date_lag').is_null())
                | ((pl.col('date') - pl.col('date_lag')).dt.total_days() > 7)
            )
            .drop('date_lag', 'pcs_lag')
        )  # fmt: skip

        # Keep records whose POS value is greater than Q1 value
        pos = (
            pos
            .with_columns(
                pl.col('pcs').quantile(.25).over('restaurant', 'meal_id', order_by='date').alias('pcs_q1')
            )
            .filter(pl.col('pcs') >= pl.col('pcs_q1'))
            .drop('pcs_q1')
        )  # fmt: skip

        # Keep records whose serving_percent is greater than THETA
        THETA = 0.48  # this is the 1st quartile of raw data
        pos = (
            pos
            .filter(pl.col('serving_percent') >= THETA)
            # .drop('serving_percent')
        )  # fmt: skip

        return pos
