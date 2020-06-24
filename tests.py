from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, Game
from config import Config
from flask import template_rendered, url_for
from flask_login import current_user
from contextlib import contextmanager

# from https://stackoverflow.com/questions/23987564/test-flask-render-template-context
@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False

class AuthModuleCase(unittest.TestCase):
    def setUp(self):
        print('Setting up!')
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, c):
        rv = c.post('/register', data={'username':'TestUser'})

    def test_user_registration(self):
        ''' tests user registration '''
        with self.app.test_client() as c:
            rv = c.get('/')
            self.assertEqual(rv.status_code, 302) # should return redirect to register page
            self.assertIn(url_for('auth.register'), rv.location)
            rv = c.get('/', follow_redirects=True)
            self.assertEqual(rv.status_code, 200)

            # let's log in
            rv = c.post(url_for('auth.register'), data={'username':'NewUser'})
            self.assertEqual(rv.status_code, 302)
            self.assertNotIn('register', rv.location)
            no_user = User.query.filter_by(username="NonexistingUser").first()
            self.assertEqual(no_user, None)
            new_user = User.query.filter_by(username="NewUser").first()
            self.assertEqual("NewUser", new_user.username)
            self.assertEqual("NewUser", current_user.username)

    def test_game_creation(self):
        ''' test creation of a game '''
        with self.app.test_client() as c:
            self.login(c)
            rv = c.get(url_for('auth.create_game'))
            self.assertEqual(rv.status_code, 200)

            rv = c.post(url_for('auth.create_game'), data=dict(name = "TestGame"), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'TestGame', rv.data)
            game = Game.query.filter_by(name="TestGame").first()
            self.assertIsNotNone(game)
            self.assertEqual(game.players[0], current_user)
            self.assertEqual(self.app.config['ROLES']['HOST'], current_user.role)
            self.assertNotEqual(self.app.config['ROLES']['PLAYER'], current_user.role)

            self.assertEqual(game.get_host(), current_user)

    def test_join_game(self):
        ''' test creation of join links '''

        # create a test game and host and store in db
        g = Game(name="TestGame")
        u = User(username="TestHost")
        g.set_host(u)
        db.session.add(g)
        db.session.add(u)
        db.session.commit()

        # test lower level token functions
        token = g.get_join_token()
        g2 = Game.verify_join_token(token)
        self.assertEqual(g, g2)

        # expired tokens should not work
        too_late_token = g.get_join_token(-10)
        g3 = Game.verify_join_token(too_late_token)
        self.assertIsNone(g3)

        with self.app.test_client() as c:
            c.get('/')
            # should be referred to login page first
            rv = c.get(url_for('auth.join_game', token=token))
            self.assertEqual(rv.status_code, 302)
            # token should be in the 'next' part of the refer url
            self.assertIn(token, rv.location)

            self.login(c)
            # fake token should not work and return 404
            rv = c.get(url_for('auth.join_game', token='SomeTokenThatDoesNotWork'))
            self.assertEqual(rv.status_code, 404)

            # right token should work and refer to the lobby
            rv = c.get(url_for('auth.join_game', token=token), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'TestGame', rv.data)
            self.assertIn(b'TestHost', rv.data)
            self.assertIn(b'TestUser', rv.data)

            # current user should be added as player
            self.assertIn(current_user, g.players)
            self.assertEqual(current_user.role, self.app.config['ROLES']['PLAYER'])
            self.assertEqual(current_user.game, g)
            self.assertEqual(g.players.count(), 2)

if __name__ == '__main__':
    unittest.main(verbosity=2)
