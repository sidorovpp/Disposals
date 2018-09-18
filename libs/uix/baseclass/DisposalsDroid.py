import urllib.request
import urllib.parse
import sys
import base64
import json

username = 'Sidorov_PP'
password = 'ppcrm123'

def ping(host):
    """
    Returns True if host responds to a ping request
    """
    import subprocess, platform

    # Ping parameters as function of OS
    ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"

    # Ping subprocess.STARTF_USESHOWWINDOW - скрывает окно
    return subprocess.call("ping " + ping_str + " " + host, shell=True) == 0


if sys.platform.startswith('linux'):
    server = '77.233.5.22'
else:
    if ping('test3'):
        server = '192.168.0.13:8085'
    else:
        server = '77.233.5.22'


# server = '192.168.0.12'

class HTTPPasswordMgrWithPriorAuth(urllib.request.HTTPPasswordMgrWithDefaultRealm):
    def __init__(self, *args, **kwargs):
        self.authenticated = {}
        super().__init__(*args, **kwargs)

    def add_password(self, realm, uri, user, passwd, is_authenticated=False):
        self.update_authenticated(uri, is_authenticated)
        # Add a default for prior auth requests
        if realm is not None:
            super().add_password(None, uri, user, passwd)
        super().add_password(realm, uri, user, passwd)

    def update_authenticated(self, uri, is_authenticated=False):
        # uri could be a single URI or a sequence
        if isinstance(uri, str):
            uri = [uri]

        for default_port in True, False:
            for u in uri:
                reduced_uri = self.reduce_uri(u, default_port)
                self.authenticated[reduced_uri] = is_authenticated

    def is_authenticated(self, authuri):
        for default_port in True, False:
            reduced_authuri = self.reduce_uri(authuri, default_port)
            for uri in self.authenticated:
                if self.is_suburi(uri, reduced_authuri):
                    return self.authenticated[uri]


def OpenJsonUrl(url, params={}, username=None, password=None):
    data = json.dumps(params)
    req = urllib.request.Request(url, data.encode('utf-8'))
    if username != None:

        # password_mgr = HTTPPasswordMgrWithPriorAuth()
        # top_level_url = url
        # password_mgr.add_password(None, top_level_url, username, password, is_authenticated = True)
        # handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        # handler = HTTPBasicPriorAuthHandler(password_mgr)
        # opener = urllib.request.build_opener(handler)

        s = 'Basic ' + (base64.encodebytes(('%s:%s' % (username, password)).encode())[:-1]).decode()
        req.add_header("Authorization", s)
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        # req.add_header("Content-length", "13")
        req.add_header("User-agent", "Python-urllib/3.5")

        # with opener.open(req) as response:
        # print(req.header_items())
        with urllib.request.urlopen(req) as response:
            str_response = response.read().decode('utf8')
            obj = json.loads(str_response)
    else:
        with urllib.request.urlopen(req) as response:
            str_response = response.read().decode('utf8')
            obj = json.loads(str_response)

    return obj


def GetResult(name, params={}, columns=['Name'], auth=True):
    c = []
    url = 'http://' + server + '/rest/datasnap/rest/TDisposalMethods/"' + name + '"'
    try:
        if auth:
            res = OpenJsonUrl(url, params, username, password)
        else:
            res = OpenJsonUrl(url, params)
    except urllib.error.HTTPError as e:
        print(e)
        print(e.read())
        return c
        
    try:
        for x in res['result'][0]['Data']:
            if columns == []:
                collist = [x['Title'] for x in res['result'][0]['Columns']]
            else:
                collist = columns
            item = []
            for y in collist:
                item.append(x[res['result'][0]['Columns'].index({'Title': y})])
            c.append(item)
    except:
        print('Ошибка чтения данных, результат:')
        print(res)
    return c


def GetStaff(id, Staff):
    for i in Staff:
        if i[0] == id:
            return i[1]
    return Null


def ShowTaskList(driod, Res, Staff):
    TaskList = []
    for item in Res:
        TaskList.append(
            '{0}\n{1}\n{2}\n{3}\n'.format(item[0], item[1], GetStaff(item[2], Staff), GetStaff(item[3], Staff)))

    droid.makeToast('Непрочитано: ' + str(len(TaskList)))
    droid.fullSetList('list', TaskList)


def ShowTask(droid, id, Res, Staff):
    r = False
    title = 'Задача'
    droid.dialogCreateAlert(title)

    TaskList = []
    TaskList.append(
        '{0}\n{1}\n{2}\n{3}\n'.format(Res[id][0], Res[id][4], GetStaff(Res[id][2], Staff), GetStaff(Res[id][3], Staff)))

    Notes = GetResult('getDisposalNotes', {'disposal_id': int(Res[id][0])}, ['DateCreate', 'UserName', 'Unnamed3'])
    for item in Notes:
        TaskList.append('{0}  {1}\n{2}\n'.format(item[0], item[1], item[2]))
    droid.dialogSetItems(TaskList)
    droid.dialogSetNeutralButtonText('Ответить')
    droid.dialogSetPositiveButtonText('Прочитано')
    droid.dialogSetNegativeButtonText('Не читать')
    droid.dialogShow()
    response = droid.dialogGetResponse().result
    if 'which' in response:
        r = response['which'] != 'negative'
        if response['which'] == 'neutral':
            text = droid.dialogGetInput("Сообщение", "Введите новое сообщение", "").result
            if text != None:
                k = {'disposal_id': int(Res[id][0]), 'comment': text}
                GetResult('SendComment', k, [], True)
    elif 'item' in response:
        droid.setClipboard(TaskList[response['item']])
    return r


def eventloop():
    while True:
        event = droid.eventWait(50).result
        if event != None:
            # print(event)
            if event["name"] == "key":
                droid.vibrate(30)
                if event["data"]["key"] == '4':
                    return
                elif event["data"]["key"] == '24':
                    pass
                elif event["data"]["key"] == '25':
                    pass
            elif event["name"] == "click":
                droid.vibrate(30)
                id = event["data"]["id"]
                if id == "closebutton":
                    return
            elif event["name"] == "itemclick":
                droid.vibrate(30)
                pos = event["data"]["position"]
                if ShowTask(droid, int(pos), res, resStaff) == True:
                    GetResult('SetTaskRead', {'id': int(res[int(pos)][0])}, [], True)
            elif event["name"] == "screen":
                if event["data"] == "destroy":
                    return

