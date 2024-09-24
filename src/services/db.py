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

fetch_infos = {
    "biowaste": [],
    "co2": [],
    "pieces_whole": ["date", "restaurant"],
    "pieces_per_dish": ["date"],
    "dishes": [],
    "menu": ["date", "restaurant"],
}


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
def fetch(table_name: str, **kwargs):
    assert table_name in fetch_infos
    requires = fetch_infos[table_name]

    # Compose SQL
    query = """
        select
            *
        from
            {table}
        where 1=1
    """
    for r in requires:
        query += f" and {r} = {{{r}}}"
    query += ";"

    # logger.debug(query)

    # Trigger query
    cur = kwargs["cur"]

    stmt = sql.SQL(query).format(
        table=sql.Identifier(table_name), **{r: kwargs[r] for r in requires}
    )
    cur.execute(stmt)

    ret = cur.fetchall()
    ret = pd.DataFrame.from_records(ret)

    return ret
