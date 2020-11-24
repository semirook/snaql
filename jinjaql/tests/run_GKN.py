import os
from jinjaql.factory import JinJAQL
import jinjaql.engine as engine
import pathlib
import pandas as pd
import pyodbc
import timeit

def nwt_engine(query_string: str, connection_string: str):
    """
    :param query_string: The raw query string to execute
    :param connection: Connection string formatted for use by PYODBC
    :return: A pandas DataFrame
    """
    connection = pyodbc.connect(connection_string)
    try:
        return pd.read_sql_query(query_string, connection)
    except Exception as e:
        print(e)
    finally:
        connection.close()

sql_root = pathlib.Path(r'C:\Users\david.smit\PycharmProjects\jinjaql\jinjaql\tests\queries')

snaql = JinJAQL(sql_root, engine=nwt_engine, cache=True)

gkn_queries = snaql.load_queries('GKN_query.sql')
context = {
    'database':'C1_RDM',
    'station':'View_Station440',
    'top':100,
}

def test_query():
    gkn_queries.top_ten(**context)

total_time = timeit.timeit(test_query, number=5)
print(total_time)