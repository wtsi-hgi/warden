import json
import urllib.request
import datetime

import flask

app = flask.Flask(__name__)

# timestamp of when Warden last checked Arboretum's modification time
LAST_CHECKED = datetime.datetime.min
# group:IP mapping for active instances
ACTIVE_INSTANCES = {}

@app.route('/')
def index():
    # forces an update as soon as the page is opened
    global LAST_CHECKED
    LAST_CHECKED = datetime.datetime.min

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

        global ACTIVE_INSTANCES
        ACTIVE_INSTANCES = {}
        for name, group in groups.items():
            if group['status'] == "up":
                ACTIVE_INSTANCES[name] = group['instance_ip']

        LAST_CHECKED = datetime.datetime.now()
        return groups
    else:
        # double quoted to be valid json (which this function is expected to
        # return)
        return '"OK"'

@app.route('/view/<group>/<path:path>')
def proxy(group, path):
    global ACTIVE_INSTANCES
    if group not in ACTIVE_INSTANCES.keys():
        return 'NOT ACTIVE'
    else:
        group_ip = ACTIVE_INSTANCES[group]

    group_url = "http://{}/{}".format(group_ip, path)

    if path[:3] == "api":
        # Treeserve's API parameters get caught by Flask, so the URL has to
        # be reconstructed
        depth = flask.request.args.get('depth')
        directory = flask.request.args.get('path')
        group_url = "{}?depth={}&path={}".format(group_url, depth, directory)

    if flask.request.method=='GET':
        resp = urllib.request.urlopen(group_url)
        excluded_headers = ['content-encoding', 'content-length',
            'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.getheaders()
            if name.lower() not in excluded_headers]
        code = resp.code
        content = resp.read()

        if path[:3] == "api":
            response = flask.Response(content, code, headers,
                mimetype="application/json")
        else:
            response = flask.Response(content, code, headers)

        return response

    elif flask.request.method=='POST':
        resp = urllib.request.Request(group_url, json=flask.request.get_json())
        excluded_headers = ['content-encoding', 'content-length',
            'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.getheaders()
            if name.lower() not in excluded_headers]
        code = resp.code
        content = resp.read()
        response = flask.Response(content, code, headers)
        return response
