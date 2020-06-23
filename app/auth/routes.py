from app import db
from app.auth import bp
from app.auth.forms import RegistrationForm
from app.models import User
#from app.auth.email import send_password_reset_email
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from datetime import datetime
from flask_babel import _

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Welcome, %(username)s', username=user.username))
        login_user(user, remember=1)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/register.html', title=_('Welcome'), form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    ''' Request a password reset if email is correct '''

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('An email with instructions has been sent')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password_request.html', title="Reset password", form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    ''' resets the password '''
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Password reset!')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title="Reset password", form=form)
