import urllib.request
import urllib.parse
from urllib.error import HTTPError
import base64
import json


# if sys.platform.startswith('linux'):
#    server = '77.233.5.22'
# else:
#    if ping('test3'):
#        server = '192.168.0.13:8085'
#    else:
#        server = '77.233.5.22'


# server = '192.168.0.12'

def ping(host):
    """
    Returns True if host responds to a ping request
    """
    import subprocess, platform

    # Ping parameters as function of OS
    ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"

    # Ping subprocess.STARTF_USESHOWWINDOW - скрывает окно
    return subprocess.call("ping " + ping_str + " " + host, shell=True) == 0


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


def OpenJsonUrl(url, params={}, username=None, password=None, headers={}, res_headers={}):
    data = json.dumps(params)
    req = urllib.request.Request(url, data.encode('utf-8'))

    # если переданы заголовки - копируем
    if len(headers) != 0:
        for i in headers.keys():
            req.add_header(i, headers[i])

    if username != None:
        s = 'Basic ' + (base64.encodebytes(('%s:%s' % (username, password)).encode())[:-1]).decode()
        req.add_header("Authorization", s)
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        req.add_header("User-agent", "Python-urllib/3.5")

    # запрашиваем данные
    with urllib.request.urlopen(req) as response:
        str_response = response.read().decode('utf8')
        obj = json.loads(str_response)

        # считываем заголовки в ответе
        info = response.info()
        res_headers.clear()
        for i in info.keys():
            res_headers[i] = info[i]

    return obj


class ConnectManager():
    # доступ пользователя
    username = ''
    password = ''
    server = ''
    sms = ''
    current_pragma = ''
    StaffID = None

    # системный доступ
    sysusername = ''
    syspassword = ''

    #инициализируем коненкт, если СМС доступ - проверяем правильность, получаем прагму
    def InitConnect(self):
        headers = {}
        #стандартная аутентификация
        if self.sms == '':
            url = 'http://' + self.server + '/rest/datasnap/rest/TDisposalMethods/"getStaffID"'
            res = OpenJsonUrl(url, {}, username=self.username, password=self.password, res_headers=headers)

            self.current_pragma = headers['Pragma'][:headers['Pragma'].find(',')]
        #через СМС
        else:
            url = 'http://' + self.server + '/rest/datasnap/rest/TSysMethods/"getUser"'
            res = OpenJsonUrl(url, {'name': self.username, 'code': self.sms}, username=self.sysusername + '$' + self.username, password=self.syspassword, res_headers=headers)
            if len(res['result'][0]['Data']) == 0:
                self.current_pragma = ''
            else:
                self.current_pragma = headers['Pragma'][:headers['Pragma'].find(',')]

    def GetIndexByName(self, collist, caption, name):
        i = -1
        for i in range(0, len(collist)):
            if collist[i][caption].lower() == name.lower():
                return i
        return i

    def GetResult(self, name, params={}, columns=['Name'], auth=True, prefix='TDisposalMethods'):

        c = []

        url = 'http://' + self.server + '/rest/datasnap/rest/' + prefix + '/"' + name + '"'

        if auth:
            #если не pragma пусто - инициализируем
            if self.current_pragma == '':
                self.InitConnect()

            if self.current_pragma == '':
                raise NameError('Connect initialization error.')

            headers = {}
            headers['Pragma'] = self.current_pragma

            try:
                #пока добавляю username=self.username, password=self.password -сломалась прагма
                #убрал, заработало
                res = OpenJsonUrl(url, params, headers=headers)
                # при ошибке 403 пробуем переинициализировать коннет и запросить ещё раз
            except HTTPError as error:
                if error.code == 403:
                    self.InitConnect()
                    headers['Pragma'] = self.current_pragma
                    # пока добавляю username=self.username, password=self.password -сломалась прагма
                    # убрал, заработало
                    res = OpenJsonUrl(url, params, headers=headers)
                else:
                    raise error
        else:
            res = OpenJsonUrl(url, params)

        #если не массив - то возвращаю значение
        if not type(res['result'][0]) is dict:
            return res['result'][0]
        else:
            if 'Data' in res['result'][0]:
                for x in res['result'][0]['Data']:
                    if columns == []:
                        collist = [x['Title'] for x in res['result'][0]['Columns']]
                    else:
                        collist = columns
                    item = []
                    for y in collist:
                        i = self.GetIndexByName(res['result'][0]['Columns'], 'Title', y)
                        if i != -1:
                            item.append(x[i])
                        else:
                            item.append('empty')
                    c.append(item)
            else:
                if 'Result' in res['result'][0]:
                    c.append(res['result'][0]['Result'])
                else:
                    c.append(res['result'][0]['id'])


        return c


connect_manager = ConnectManager()



