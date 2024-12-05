import os

import pandas as pd
import psycopg as pg
from loguru import logger
from psycopg import sql
from psycopg.rows import dict_row

USER = os.getenv("DB_USER", None)
PWD = os.getenv("DB_PWD", None)
PORT = os.getenv("DB_PORT", None)
HOST = os.getenv("DB_HOST", None)
DB_NAME = os.getenv("DB_NAME", None)


def db_connect(func):
    def func_inner(*args, **kwargs):
        try:
            with pg.connect(
                user=USER,
                password=PWD,
                host=HOST,
                port=PORT,
                dbname=DB_NAME,
                row_factory=dict_row,
            ) as conn:
                with conn.cursor() as cur:
                    return func(cur=cur, conn=conn, *args, **kwargs)

        except pg.OperationalError as e:
            logger.error(f"Connect to DB got error: {e}")

            return None

    return func_inner


@db_connect
def fetch_menu(table_name: str = "menu", **kwargs) -> pd.DataFrame:
    query = """
        with tmp1 as (
            select
                restaurant
                , index
                , sum(fitness) as fitness
            from {table}
            where 1=1
                and restaurant = {restaurant}
                and "date" < {date_to}
                and "date" >= {date_from}
            group by restaurant, index
            order by fitness
            limit {num_rows}
        ), tmp2 as (
            SELECT
                *,
                rank() over (PARTITION BY restaurant order by fitness) as rank
            from tmp1
        )
            select
                {table}.index,
                date,
                {table}.restaurant,
                meal_ids,
                {table}.fitness,
                tmp2.rank
            from {table}
            JOIN tmp2 ON 1=1
                and {table}.restaurant = tmp2.restaurant
                and {table}.index = tmp2.index
            where 1=1
                and {table}.restaurant = {restaurant}
                and {table}.date < {date_to}
                and {table}.date >= {date_from}
            ORDER BY rank, date
        ;
    """

    # Trigger query
    cur = kwargs["cur"]

    stmt = sql.SQL(query).format(
        table=sql.Identifier(table_name),
        restaurant=sql.Literal(kwargs["restaurant"]),
        date_to=sql.Literal(kwargs["date_to"]),
        date_from=sql.Literal(kwargs["date_from"]),
        num_rows=sql.Literal(kwargs["num_rows"]),
    )
    # logger.debug(stmt.as_string())

    cur.execute(stmt)

    ret = cur.fetchall()
    out = pd.DataFrame.from_records(ret)

    return out


@db_connect
def fetch_meal_info(
    table1: str = "meal_names", table2: str = "meals", **kwargs
) -> pd.DataFrame:
    query = """
        with tmp as (
            SELECT
                meal_id
                , meal
                , rank() over (PARTITION BY meal_id order by meal) as rank
            from {table1}
        ), tmp1 as (
            SELECT meal_id, meal from tmp where rank = 1
        )
        select
            {table2}.meal_id
            , {table2}.meal_type_1 as meal_type
            , {table2}.is_kela as is_kela
            , tmp1.meal as name
        from {table2}
        JOIN tmp1
        ON  {table2}.meal_id = tmp1.meal_id
        where 1=1
            and {restaurant} = any({table2}.restaurant)
            and {table2}.schoolyear = {schoolyear}
        ;
    """

    # Trigger query
    cur = kwargs["cur"]

    stmt = sql.SQL(query).format(
        table1=sql.Identifier(table1),
        table2=sql.Identifier(table2),
        restaurant=sql.Literal(kwargs["restaurant"]),
        schoolyear=sql.Literal(kwargs["schoolyear"]),
    )
    # logger.debug(stmt.as_string())

    cur.execute(stmt)

    ret = cur.fetchall()
    out = pd.DataFrame.from_records(ret)

    return out


@db_connect
def fetch_meal_info_with_ids(table: str = "meals", **kwargs) -> pd.DataFrame:
    query = """
        select
            meal_id as "id"
            , meal_type_1 as type
            , pcs_mean as "mean"
            , is_kela
        from {table}
        where meal_id = ANY(%s)
        ;
    """

    # Trigger query
    cur = kwargs["cur"]

    stmt = sql.SQL(query).format(table=sql.Identifier(table))
    # logger.debug(stmt.as_string())

    cur.execute(stmt, [(kwargs["meal_ids"])])

    ret = cur.fetchall()
    out = pd.DataFrame.from_records(ret)

    return out


@db_connect
def fetch_co2_with_ids(table: str = "co2", **kwargs) -> pd.DataFrame:
    query = """
        select
            meal_id
            , co2
        from {table}
        where meal_id = ANY(%s)
        ;
    """

    # Trigger query
    cur = kwargs["cur"]

    stmt = sql.SQL(query).format(table=sql.Identifier(table))
    # logger.debug(stmt.as_string())

    cur.execute(stmt, [(kwargs["meal_ids"])])

    ret = cur.fetchall()
    out = pd.DataFrame.from_records(ret)

    return out


@db_connect
def fetch_waste_with_ids(table: str = "biowaste", **kwargs) -> pd.DataFrame:
    query = """
        select
            meal_id
            , waste
        from {table}
        where meal_id = ANY(%s)
        ;
    """

    # Trigger query
    cur = kwargs["cur"]

    stmt = sql.SQL(query).format(table=sql.Identifier(table))
    # logger.debug(stmt.as_string())

    cur.execute(stmt, [(kwargs["meal_ids"])])

    ret = cur.fetchall()
    out = pd.DataFrame.from_records(ret)

    return out


@db_connect
def fetch_pos_whole(table: str = "pieces_whole", **kwargs) -> dict:
    query = """
        select
            date
            , restaurant
            , pcs as pcs_whole
        from {table}
        where restaurant = {restaurant} and date = {date}
        ;
    """

    # Trigger query
    cur = kwargs["cur"]

    stmt = sql.SQL(query).format(
        table=sql.Identifier(table),
        restaurant=sql.Literal(kwargs["restaurant"]),
        date=sql.Literal(kwargs["date"]),
    )

    cur.execute(stmt)

    out = cur.fetchone()

    return out
