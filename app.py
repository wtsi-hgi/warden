import json
import urllib.request
import datetime

import flask

app = flask.Flask(__name__)

# group:IP mapping for active instances
ACTIVE_INSTANCES = {}

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
    js_stamp = flask.request.args.get('stamp')
    req = urllib.request.urlopen("http://localhost:8000/lastmodified")

    arboretum_stamp = json.loads(req.read())

    if js_stamp != arboretum_stamp:
        req = urllib.request.urlopen("http://localhost:8000/groups")
        groups = json.loads(req.read())

        response = {'stamp': arboretum_stamp, 'groups': groups}

        global ACTIVE_INSTANCES
        ACTIVE_INSTANCES = {}
        for name, group in groups.items():
            if group['status'] == "up":
                ACTIVE_INSTANCES[name] = group['instance_ip']

        return response
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
