from app import db
from app.auth import bp
from app.auth.forms import UserRegistrationForm, CreateGameForm
from app.models import User, Game
from flask import render_template, flash, redirect, url_for, request, abort, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import re, json
from datetime import datetime
from flask_babel import _

@bp.route('/')
@bp.route('/index')
@login_required
def lobby():
    # delete all notifications of new players joining
    current_user.notifications.filter_by(name='new_player_joined').delete()
    db.session.commit()

    # render template
    return render_template('auth/lobby.html', title="Welcome in the lobby")

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.lobby'))

    # check if join token is in the next page to pass on to username validation
    game = None
    next_page = request.args.get('next')
    if next_page is not None:
        token_search = re.search('/join_game/(.+)', next_page)
        if token_search:
            game = Game.verify_join_token(token_search.groups()[0])
    form = UserRegistrationForm(game)
    if form.validate_on_submit():
        user = User(username=form.username.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Welcome, %(username)s', username=user.username))
        login_user(user, remember=1)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('auth.lobby')
        return redirect(next_page)
    return render_template('auth/register.html', title=_('Welcome'), form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.lobby'))

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
        return redirect(url_for('auth.lobby'))

    return render_template('auth/create_game.html', form=form, title='Create game')

@bp.route('/join_game/<token>')
@login_required
def join_game(token):
    g = Game.verify_join_token(token)
    if g is None:
        abort(404)
    # add notifications for all other users
    for player in g.players.all():
        player.add_notification('new_player_joined', {'username' : current_user.username})

    # add game to current user
    current_user.game = g
    if not current_user.role == current_app.config['ROLES']['HOST']:
        current_user.role = current_app.config['ROLES']['PLAYER']
        flash(_('You joined %(game_name)s as a player', game_name=g.name))
    else:
        flash(_('You are the host of %(game_name)s', game_name=g.name))
    db.session.commit()
    return redirect(url_for('auth.lobby'))
