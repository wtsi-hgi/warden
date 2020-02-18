import json
import urllib.request
import datetime

import flask

app = flask.Flask(__name__)

# timestamp of when Warden last checked Arboretum's modification time
LAST_CHECKED = datetime.datetime.now()

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

@app.route('/update')
def getGroupTable():
    req = urllib.request.urlopen("http://localhost:8000/lastmodified")

    result = json.loads(req.read())
    last_modified = datetime.datetime.strptime(result, "%Y-%m-%d %H:%M:%S")

    global LAST_CHECKED
    if last_modified > LAST_CHECKED:
        req = urllib.request.urlopen("http://localhost:8000/groups")
        groups = json.loads(req.read())
        LAST_CHECKED = datetime.datetime.now()
        return groups
    else:
        return '"OK"'
