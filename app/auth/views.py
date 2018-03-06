from . import auth
from .. import db
from flask import render_template, request, url_for, redirect, flash, current_app
from .forms import LoginForm, RegistrationForm
from ..models import User
from ..email import send_email
from flask_login import login_user, logout_user, login_required, current_user

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #email = form.email.data
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid email or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        send_email(current_app.config['MAIL_ADMIN'], 'Confirm Your Account',
                   'auth/mail/confirm', user=user, token=user.generate_confirmation_token())
        flash('A confirmation email has been set to your register email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.before_app_request
def please_confirm():
    if current_user.is_authenticated and not current_user.confirmed and \
        request.blueprint != 'auth' and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect('main.index')
    return render_template('auth/unconfirmed.html')


@auth.route('/reconfirm')
@login_required
def resend_confirmation():
    if current_user.confirmed:
        flash('your account had been confirmed.')
        redirect(url_for('main.index'))
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/mail/confirm', user=current_user, token=token)
    flash('A new confirmation email has been set to your register email.')
    return redirect(url_for('auth.login'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()     # commit user confirmed status change to db
        flash('You have confirmed your account. Thanks.')
    else:
        flash('The confimation link is expired or invalid.')
    return redirect(url_for('main.index'))

