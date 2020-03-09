import json
import urllib.request
import datetime
import base64
import ldap

import flask

app = flask.Flask(__name__, static_url_path="/treeserve/static")

# group:IP mapping for active instances
ACTIVE_INSTANCES = {}

def isUserHumgen():
    auth = flask.request.cookies.get('nginxauth')
    # base64 -> byte string -> Python string
    username = base64.b64decode(auth).decode('UTF-8').split(':')[0]

    conn = ldap.initialize("ldap://ldap-ro.internal.sanger.ac.uk:389")
    conn.bind('','')

    result = conn.search_s("ou=people,dc=sanger,dc=ac,dc=uk",
        ldap.SCOPE_ONELEVEL, "(uid={})".format(username), ['sangerBomArea'])

    # extracts user's BoM area from the LDAP results object
    area = result[0][1]['sangerBomArea'][0].decode('UTF-8')

    if area == "Human Genetics":
        return True
    else:
        return False

@app.route('/treeserve/')
def index():
    if not isUserHumgen():
        return 'Sorry, Human Genetics faculty only.'

    req = urllib.request.urlopen("http://localhost:8000/groups")

    groups = json.loads(req.read())

    resp = flask.make_response(
        flask.render_template('index.html', groups=groups))
    # cookie stops POST requests from doing anything unless the user visits
    # the root page first
    resp.set_cookie('warden_active_session', 'humgen')
    return resp

@app.route('/treeserve/create/<group>', methods = ['POST'])
def createInstance(group):
    if not flask.request.cookies.get('warden_active_session'):
        return 'This URL should not be accessed directly.'

    req = urllib.request.urlopen("http://localhost:8000/create?group={}"
        .format(group))

    return 'OK'

@app.route('/treeserve/destroy/<group>', methods = ['POST'])
def destroyInstance(group):
    if not flask.request.cookies.get('warden_active_session'):
        return 'This URL should not be accessed directly.'

    req = urllib.request.urlopen("http://localhost:8000/destroy?group={}"
        .format(group))

    return 'OK'

@app.route('/treeserve/update')
def getGroupTable():
    if not flask.request.cookies.get('warden_active_session'):
        return 'This URL should not be accessed directly.'

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

@app.route('/treeserve/view/<group>/<path:path>')
def proxy(group, path):
    if not isUserHumgen():
        return 'Sorry, Human Genetics faculty only.'

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
