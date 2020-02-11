import json
import urllib.request

import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
    req = urllib.request.urlopen("http://localhost:8000/groups")

    groups = json.loads(req.read())

    return flask.render_template('index.html', groups=groups)

@app.route('/create/<group>')
def createInstance(group):
    req = urllib.request.urlopen("http://localhost:8000/create?group={}"
        .format(group))

    return 'OK'

@app.route('/destroy/<group>')
def destroyInstance(group):
    req = urllib.request.urlopen("http://localhost:8000/destroy?group={}"
        .format(group))

    return 'OK'
