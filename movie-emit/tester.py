import os
import sqlite3

path = os.path.abspath('.')+"\movie.db"
con=sqlite3.connect(path)
cur = con.cursor()

# cur.execute(r'CREATE TABLE movie (movie_name varchar(255),desc varchar(255),store_path varchar(255) )')

def query():
    r = cur.execute("select * from movie")
    for line in r:
        print(line)
con.close()

if __name__ == '__main__':
    query()

