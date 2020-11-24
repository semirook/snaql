from jinjaql.factory import JinJAQL
import pandas as pd
import pyodbc
import functools
import pathlib

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


factory = JinJAQL(folder_path=pathlib.Path(''), engine=nwt_engine, cache=functools.lru_cache)
query = factory.load_queries('GKN_test.sql')

print(query.station_data(database='C1_RDM',station='View_Station440', ))
print(query.station_data(database='C1_RDM',station='View_Station440', ))
print(query.sta440())
print(query.sta440())