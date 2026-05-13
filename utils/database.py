import sqlite3
import pandas as pd


def create_connection(database_path):
    """
    Create SQLite database connection
    """

    conn = sqlite3.connect(database_path)

    return conn


def run_query(query, database_path):
    """
    Execute SQL query and return DataFrame
    """

    conn = create_connection(database_path)

    df = pd.read_sql(query, conn)

    conn.close()

    return df