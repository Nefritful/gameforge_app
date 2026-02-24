import pymysql

def connect_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="dreddred",
        database="gameforge",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

def db_one(sql: str, args=()):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchone()
    finally:
        conn.close()

def db_all(sql: str, args=()):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchall()
    finally:
        conn.close()

def db_exec(sql: str, args=()):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.lastrowid
    finally:
        conn.close()
