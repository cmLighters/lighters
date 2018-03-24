from config import config
from flask import Flask
from flask_mail import Mail
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
import flask_whooshalchemyplus
#from flask_msearch import Search
#from jieba.analyse import ChineseAnalyzer

mail = Mail()
moment = Moment()
bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
pagedown = PageDown()
#search = Search(analyzer=ChineseAnalyzer())

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    flask_whooshalchemyplus.init_app(app)
    #search.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    from .inner_api import inner_api as inner_api_blueprint
    app.register_blueprint(inner_api_blueprint, url_prefix='/inner_api/v0.1')

    return app