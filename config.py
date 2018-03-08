import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.yeah.net'
    MAIL_PORT = 25
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', 1]
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFFIX = '[cmLighters\' Blog]'
    MAIL_SENDER = 'Blog mail sender <mijechen@yeah.net>'
    BLOG_ADMIN = os.environ.get('BLOG_ADMIN')
    POSTS_PER_PAGE = 10
    FOLLOWERS_PER_PAGE = 25
    COMMENTS_PER_PAGE = 15

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or \
                                             'mysql+pymysql://{username}:{password}@{hostname}/{database}'.format(
                                                 username='testuser', password='asdfjkl;', hostname='127.0.0.1',
                                                 database='cm_flask_blog'
                                             )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or \
                                             'mysql+pymysql://{username}:{password}@{hostname}/{database}'.format(
                                                 username='testuser', password='asdfjkl;', hostname='127.0.0.1',
                                                 database='test_cm_flask_blog'
                                             )


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')


config = dict(
    development = DevelopmentConfig,
    testing = TestingConfig,
    production = ProductionConfig,

    default = DevelopmentConfig
)

