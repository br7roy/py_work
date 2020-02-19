import os
import sqlite3
from flask_bootstrap import Bootstrap

from flask import Flask, render_template

app = Flask(__name__)
path = os.path.abspath('.') + os.sep + "movie.db"
bootstrap = Bootstrap(app)

@app.route('/movieDomain')
def show():

    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("select * from movie")
    rows = cur.fetchall()
    con.close()

    return render_template('index.html', rows=rows)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8089)
