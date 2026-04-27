import psycopg2
import logging


logger = logging.getLogger()


def get_db_connection(db_config: dict) -> psycopg2.extensions.connection:

    """
    Establishes a connection to the PostgreSQL database using the provided configuration.
    
    Args:
        db_config (dict): A dictionary containing database connection parameters such as host, port, dbname, user, and password.
    
    Returns:
        psycopg2.extensions.connection: A connection object to the PostgreSQL database.
    
    Raises:
        psycopg2.DatabaseError: If there is an error connecting to the database.
    """

    try:
        conn = psycopg2.connect(**db_config)
        return conn

    except psycopg2.DatabaseError as e:
        logger.error("Error connecting to the database: %s", e)
        raise
