from . import main
from .forms import NameForm
from .. import db
from ..models import User
from flask import session, redirect, url_for, render_template, current_app
from ..email import send_email


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        user = User.query.filter_by(username=name).first()
        if user is None:
            user = User(username=name)
            db.session.add(user)
            session['known'] = False
            if current_app.config['MAIL_ADMIN']:
                send_email(current_app.config['MAIL_ADMIN'], 'New user <%s> register' % name, 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = name
        form.name.data = ''
        return redirect(url_for('main.index'))
    return render_template('index.html', name=session.get('name'), known=session.get('known', False), form=form)