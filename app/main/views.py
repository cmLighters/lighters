from . import main
from .forms import NameForm
from .. import db
from ..models import User
from flask import session, redirect, url_for, render_template, current_app
from ..email import send_email


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')