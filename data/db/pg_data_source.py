import psycopg2

import config


class PgDataSource:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST
        )

    def get_cursor(self):
        return self.conn.cursor()

    def __del__(self):
        self.conn.close()
