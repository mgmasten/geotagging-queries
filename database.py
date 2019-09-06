import sqlite3
from sqlite3 import Error
import csv
import time

def create_connection(db_file):
    """ create a database connection to the SQLite database
    specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_city(conn, city):
    """
    Create a new city into the cities table
    :param conn:
    :param city:
    :return: city id
    """
    sql = ''' INSERT INTO cities(city_name,country_iso,latitude, longitude)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, city)
    conn.commit()
    return cur.lastrowid

def find_city(conn, city_name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM cities WHERE city_name=?", (city_name,))
    rows = cur.fetchall()
    return rows


def main():
    # database_file = "./pythonsqlite.db"
    database_file = './pop_limited.db'

    sql_create_cities_table = """ CREATE TABLE IF NOT EXISTS cities (
                                        id integer PRIMARY KEY,
                                        city_name text NOT NULL,
                                        country_iso text NOT NULL,
                                        latitude real NOT NULL,
                                        longitude real NOT NULL
                                    ); """

    # create a database connection
    conn = create_connection(database_file)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_cities_table)
        print('Table created')
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
