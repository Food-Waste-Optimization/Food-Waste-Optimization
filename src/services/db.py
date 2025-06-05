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
def fetch_menu(table_menus: str = "menus", table_meals_planned: str = "meals_planned", **kwargs) -> pd.DataFrame:
    query = """
        select
            t2.weeklevel_idx
            ,to_char(date, 'YYYY-MM-DD') as date
            ,avg(t2.score) as score
            ,array_agg(t3.meal) as meal_ids
        from
            {menus} t1 
        JOIN (
            select
                weeklevel_idx
                , score
            from
                {menus}
            where 1=1
                and restaurant = {restaurant}
                and date = {date_from}
            order by score
            limit {num_rows}
        ) t2 on 1=1
            and t1.weeklevel_idx = t2.weeklevel_idx
        left JOIN {meals_planned} t3 on 1=1
            and t3.menu_id = t1.id

        GROUP BY t2.weeklevel_idx, date
        ORDER BY score, date
        ;
    """

    # Trigger query
    cur = kwargs["cur"]

    stmt = sql.SQL(query).format(
        menus=sql.Identifier(table_menus),
        meals_planned=sql.Identifier(table_meals_planned),
        restaurant=sql.Literal(kwargs["restaurant"]),
        date_from=sql.Literal(kwargs["date_from"]),
        num_rows=sql.Literal(kwargs["num_rows"]),
    )
    # logger.debug(stmt.as_string())

    cur.execute(stmt)

    ret = cur.fetchall()
    out = pd.DataFrame.from_records(ret)

    return out


@db_connect
def fetch_meal_info(table: str = "dim_meals", table_dim_meal_types: str = "dim_meal_types", **kwargs) -> pd.DataFrame:
    query = """
        select
            t1.id as meal_id
            , t2.meal_type_en as meal_type
            , t1.names as name
            , t1.attributes
        from {table} t1
        left join {table_dim_meal_types} t2 on 1=1
            and t1.meal_type = t2.meal_type_id
        ;
    """

    # Trigger query
    cur = kwargs["cur"]

    stmt = sql.SQL(query).format(
        table=sql.Identifier(table),
        table_dim_meal_types=sql.Identifier(table_dim_meal_types),
    )
    # logger.debug(stmt.as_string())

    cur.execute(stmt)

    ret = cur.fetchall()
    out = pd.DataFrame.from_records(ret)

    return out


@db_connect
def fetch_meal_info_with_restaurant(
    table: str = "dim_meals", table_dim_meal_types: str = "dim_meal_types", **kwargs
) -> pd.DataFrame:
    query = """
        select
            t1.id as meal_id
            , t2.meal_type_en as meal_type
            , t1.names[1] as name
            , t1.attributes
        from {table} t1
        left join {table_dim_meal_types} t2 on 1=1
            and t1.meal_type = t2.meal_type_id
        where 1=1
            and {restaurant} = any(t1.restaurants)
            and t1.schoolyear = {schoolyear}
        ;
    """

    # Trigger query
    cur = kwargs["cur"]

    stmt = sql.SQL(query).format(
        table=sql.Identifier(table),
        table_dim_meal_types=sql.Identifier(table_dim_meal_types),
        restaurant=sql.Literal(kwargs["restaurant"]),
        schoolyear=sql.Literal(kwargs["schoolyear"]),
    )
    # logger.debug(stmt.as_string())

    cur.execute(stmt)

    ret = cur.fetchall()
    out = pd.DataFrame.from_records(ret)

    return out


@db_connect
def fetch_meal_info_with_ids(
    table: str = "dim_meals", table_dim_meal_types: str = "dim_meal_types", **kwargs
) -> pd.DataFrame:
    query = """
        select
            t1.id as "id"
            , t1.names
            , t1.restaurants
            , t1.meal_type
            , t2.meal_type_en as meal_type_str
            , t1.attributes
            , t1.co2
        from {table} t1
        left join {table_dim_meal_types} t2 on 1=1
            and t1.meal_type = t2.meal_type_id
        where id = ANY({meal_ids})
        ;
    """

    # Trigger query
    cur = kwargs["cur"]

    stmt = sql.SQL(query).format(
        table=sql.Identifier(table),
        meal_ids=sql.Literal(kwargs["meal_ids"]),
        table_dim_meal_types=sql.Identifier(table_dim_meal_types),
    )
    # logger.debug(stmt.as_string())

    cur.execute(stmt)

    ret = cur.fetchall()
    out = pd.DataFrame.from_records(ret)

    return out


@db_connect
def fetch_restaurant_info(table: str = "dim_restaurants", **kwargs) -> dict:
    query = """
        select
            restaurant_id
            , restaurant
            , restaurant_short
        from {table}
        where POSITION(LOWER({restaurant}) in LOWER(restaurant)) > 0
        ;
    """

    # Trigger query
    cur = kwargs["cur"]

    stmt = sql.SQL(query).format(
        table=sql.Identifier(table),
        restaurant=sql.Literal(kwargs["restaurant"]),
    )

    # logger.debug(stmt.as_string())
    cur.execute(stmt)

    out = cur.fetchone()

    return out
