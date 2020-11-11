import pyodbc
import pandas as pd

def default(query_string: str, connection_string: str):
    """
    :param query_string: This is the raw query string that the SQL engine would use to return the data
    :param connection: This is the connection string that comes from the SQL template that can be used for the SQL query
    :return: The default will return the string w/o changes to keep the default SNAQL behavior, but any additional
    would return data (ie DataFrame)
    """
    return query_string


def pandas(query_string: str, connection_string: str):
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

