import sqlite3


def create_connection():
    return sqlite3.connect('db/db.sqlite')
