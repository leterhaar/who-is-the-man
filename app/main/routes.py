from app.main import bp
from app import db
from flask import render_template, request, jsonify, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from wtforms import TextField
from app.models import Notification, Setting
from app.main.forms import SettingsForm, SelectTeamsForm
from flask_babel import _

@bp.route('/notifications')
@login_required
def notifications():
    ''' retrieves notifications for current users as JSON '''
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])

@bp.route('/init_game', methods=['POST','GET'])
@login_required
def init_game():
    ''' shows a page to start the game with the settings '''

    # redirect back to lobby if the current user is not a host
    if not current_user.is_host():
        return redirect(url_for('auth.lobby'))

    game = current_user.game
    form = SettingsForm()

    # submit settings to db if form submitted
    if form.validate_on_submit():
        # delete all existing settings
        game.settings.delete()
        for setting in ['num_cars','num_rounds','round_time']:
            game.setting(key=setting, value=form[setting].data)
        db.session.commit()
        flash(_('All set up - now select the teams and we\'re good to go!'))
        return redirect(url_for('main.select_teams'))

    return render_template('main/init_game.html', form=form, title="Setting up game")

@bp.route('/select_teams', methods=['POST','GET'])
@login_required
def select_teams():
    ''' selects the teams '''

    # redirect back to lobby if the current user is not a host
    if not current_user.is_host():
        return redirect(url_for('auth.lobby'))

    form = SelectTeamsForm()

    players = current_user.game.players.all()
    for player in players:
        setattr(form, 'player_' + str(player.id), TextField(player.username))

    if form.validate_on_submit():
        pass

    return render_template('main/select_teams.html', title="Select teams", form=form)


@bp.route('/enter_cards')
@login_required
def enter_cards():
    return 'Entering cards...'
