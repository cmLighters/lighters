from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '<h3>Hello Flask</h3>'

@app.route('/user/<username>')
def user(username):
    return 'Hello, %s' % username


