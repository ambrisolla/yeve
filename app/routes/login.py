from crypt import methods
from app import yeve
from flask import Flask, render_template, request, session
import datetime
import os

@yeve.route("/", methods=['POST', 'GET'])
def login():
    args = request.args
    login = ''
    message = ''
    if 'login' in args:
        args_post = request.form
        if 'access_key' in args_post:
            if os.environ['YEVE_ACCESS_KEY'] == args_post['access_key']:
                message = 'logado'
                login = True
                session['access_key'] = args_post['access_key']
            else:
                message = 'access denied'
                login = False
    return render_template('index.html', login=login, message=message)