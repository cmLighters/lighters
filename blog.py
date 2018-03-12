import os
from flask_migrate import Migrate
from app import create_app, db, search
from app.models import Role, User, Permission, Post, Follow, Comment

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, search=search, Role=Role, User=User,
                Permission=Permission, Post=Post, Follow=Follow, Comment=Comment)


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
