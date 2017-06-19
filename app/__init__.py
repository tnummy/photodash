from flask import Flask, render_template
# from flask_mysqldb import MySQL
# from flask.ext.sqlalchemy import SQLAlchemy
from flaskext.mysql import MySQL

app = Flask(__name__)
app.config.from_object('app.config')
# mysql = MySQL(app)

mysql = MySQL()
mysql.init_app(app)
# db = SQLAlchemy(app)


@app.errorhandler(404)
def not_found(error):
  return render_template('404.html'), 404

from app.core.views import mod as core
app.register_blueprint(core)

# Later on you'll import the other blueprints the same way:
#from app.comments.views import mod as commentsModule
#from app.posts.views import mod as postsModule
#app.register_blueprint(commentsModule)
#app.register_blueprint(postsModule)

