def default(query_string: str, connection_string: str):
    """
    :param query_string: This is the raw query string that the SQL engine would use to return the data
    :param connection: This is the connection string that comes from the SQL template that can be used for the SQL query
    :return: The default will return the string w/o changes to keep the default SNAQL behavior, but any additional
    would return data (ie DataFrame)
    """
    return query_string

