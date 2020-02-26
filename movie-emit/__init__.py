from flask import Flask

# 导入各个模块
from view import movie
from .config import conf

app = Flask(__name__)
app.register_blueprint(movie)

app.config.from_object(conf)
