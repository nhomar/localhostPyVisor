# -*- coding: utf-8 -*-

import os
import mailbox

from functools import wraps
from flask import request, session, flash, Response, redirect, url_for, Flask, render_template, send_from_directory

from . import conf

app = Flask(__name__)
app.config.from_object(conf)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def _entries():
    fol = app.config['MAILFOLDER']
    usr = app.config['USERNAME']
    fullpath = os.path.join(fol, usr)
    entries = []
    for m in mailbox.mbox(fullpath):
        print type(m)
        entry = m
        entries.append(entry)
    return entries

@app.route('/')
@requires_auth
def catch_all():
    return render_template('show_entries.html', entries=_entries(), dir=dir)

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == app.config['USERNAME'] and password == app.config['PASSWORD']

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('/'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
