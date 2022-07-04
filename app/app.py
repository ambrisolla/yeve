from flask import Flask, session, request
import os
yeve = Flask(__name__)
yeve.secret_key = 'bla'

@yeve.before_request
def before_request_func():
    
    rules = [
      '/static/index.css',
      '/static/home.css'
    ]
    for rule in yeve.url_map.iter_rules():   
        rules.append(str(rule))
    if request.path not in rules:
        return {
            'status'  : 400,
            'message' : 'Invalid path!'
        },400
    permissive_list = [
        '/',
        '/static/index.css',
        '/static/home.css'
    ]
    if request.path not in permissive_list:
      if 'access_key' in session:
        if session['access_key'] == os.environ['YEVE_ACCESS_KEY']:
          pass
        else:
          return 'access denied!'
      else:
        return 'access denied!'


import routes.login
import routes.home