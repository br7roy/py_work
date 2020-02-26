from flask import Flask

from config import conf
from view import movie

app = Flask(__name__)
app.config.from_object(conf)

app.register_blueprint(movie)

if __name__ == '__main__':
    # app.run(host='127.0.0.1', port=8089)
    app.run(threaded = True)

