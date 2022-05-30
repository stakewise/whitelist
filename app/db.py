import sqlite3

from app.config import DATABASE_PATH


def setup_db():
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS requests (address text unique)""")
    con.commit()
    con.close()


def insert_record(address: str):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("insert into requests values (?)", (address,))
    con.commit()
    con.close()


def delete_record(address: str):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("delete from requests where address ='%s'" % address)
    con.commit()
    con.close()


def has_record(address: str):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("select address from requests where address ='%s'" % address)
    r = cur.fetchall()
    con.close()
    return bool(r)
