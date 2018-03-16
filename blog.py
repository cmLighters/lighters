import os
from flask_migrate import Migrate
from app import create_app, db
from app.models import Role, User, Permission, Post, Follow, Comment
from config import config

config_env = os.environ.get('FLASK_CONFIG', 'default')
app = create_app(config_env)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, config=config[config_env], Role=Role, User=User,
                Permission=Permission, Post=Post, Follow=Follow, Comment=Comment)


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
