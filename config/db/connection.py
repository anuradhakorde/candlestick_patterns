import psycopg2

def get_connection(config):
    conn = psycopg2.connect(
        host=config["db_host"],
        port=config["db_port"],
        dbname=config["db_name"],
        user=config["db_user"],
        password=config["db_password"],
    )
    return conn
