import psycopg2


def setup_db():
    conn = psycopg2.connect(database="face", user="", password="", host="127.0.0.1", port="5432")
    db = conn.cursor()
    db.execute("create extension if not exists cube;")
    db.execute("drop table if exists vectors")
    db.execute("create table vectors (id serial, username varchar,phone varchar ,mail varchar ,vec_data cube);")
    db.execute("create index vectors_vec_idx on vectors (vec_data);")
    conn.commit()
    conn.close()

setup_db()
