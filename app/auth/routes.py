from app import db
from app.auth import bp
from app.auth.forms import UserRegistrationForm, CreateGameForm
from app.models import User, Game
#from app.auth.email import send_password_reset_email
from flask import render_template, flash, redirect, url_for, request, abort, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from flask_babel import _

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = UserRegistrationForm()
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

@bp.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
    ''' Creates a game '''

    form = CreateGameForm()

    if form.validate_on_submit():
        game = Game(name=form.name.data)
        game.set_host(current_user)
        db.session.add(game)
        db.session.commit()
        flash(_('Created %(game_name)s', game_name=game.name))
        return redirect(url_for('main.index'))

    return render_template('auth/create_game.html', form=form, title='Create game')

@bp.route('/join_game/<token>')
@login_required
def join_game(token):
    g = Game.verify_join_token(token)
    if g is None:
        abort(404)
    current_user.game = g
    current_user.role = current_app.config['ROLES']['PLAYER']
    db.session.commit()
    flash(_('You joined %(game_name)s', game_name=g.name))
    return redirect(url_for('main.index'))
