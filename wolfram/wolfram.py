#encoding: utf-8
from queryBot.responsemodule import IModule
import urllib
import httplib2
import socket
import xmltodict
import re

settings_name_g = u'walpha'
api_key_g = u'api_key'
timeout_g = u'timeout'

class Wolfram(IModule):
    def __init__(self):
        self.settings = {api_key_g: None,
                         timeout_g: None}

        self.shorten_url = None
        self.last_response = u''

    def uses_settings(self):
        return True

    def get_command_patterns(self):
        return [('^\.(c|wa) (\S.*)', self.wolfAlpha)]

    def get_settings_name(self):
        return settings_name_g

    def get_configuration(self):
        return [(key, value) for (key, value) in self.settings.items() if not value is None]

    def set_configuration(self, settings):
        #fetch the settings
        for key, value in settings.items():
            if key in settings:
                self.settings[key] = value

        # signal when the module wasn't properly configured
        try:
            if self.settings[api_key_g] is None or self.settings[timeout_g] is None:
                raise ValueError

            self.settings[timeout_g] = int(self.settings[timeout_g])
        except ValueError:
            raise RuntimeError('Couldn\'t configure the module')

    def set_url_shortener(self, shortener):
        self.shorten_url = shortener.shorten_url

    # Functions that are needed for queries
    def wolfAlpha(self, nick, message, channel):
        result = self.__fetch_wolfAlpha(message)
        if result and result != self.last_response:
            self.last_response = result
            return result.encode('utf-8', errors='ignore')

    def __fetch_wolfAlpha(self, message):
        query = re.sub(r'^\.(c|wa)', u'', message.decode('utf-8'), re.UNICODE).encode('utf-8')
        query = query.strip(' \t\n\r')
        query = urllib.quote(query)
        queryurl = u'http://api.wolframalpha.com/v2/query?input={q}&appid={key}&format=plaintext&parsetimeout=0.5&formattimeout=0.5'.format(
                    q = query,
                    key = self.settings[api_key_g])

        # construct the url and shorten it if we can
        url = u'http://www.wolframalpha.com/input/?i={q}'.format(q = query)
        if not self.shorten_url is None:
            url = self.shorten_url(url)

        try:
            sock = httplib2.Http(timeout=self.settings[timeout_g])
            headers, xml_response = sock.request(queryurl)

            if headers[u'status'] in (200, '200'):
                response = xmltodict.parse(xml_response)

                int_found = False
                res_found = False

                pods = response[u'queryresult'][u'pod']

                if(response[u'@numpods'] == u'1'):
                    pods = [pods]

                for pod in pods:
                    print pod
                    # Check if we can identify pods and they have information where we can fetch it
                    if u'@id' in pod.keys() and \
                       u'subpod' in pod.keys() and u'plaintext' in pod[u'subpod'].keys():
                        if pod[u'@id'] == u'Input':
                            interpretation = pod[u'subpod'][u'plaintext']
                            int_found = True
                        elif pod[u'@id'] == u'Result':
                            result = pod[u'subpod'][u'plaintext']
                            res_found = True

                    if int_found and res_found:
                        break

                if not int_found:
                    interpretation = response[u'queryresult'][u'pod'][0][u'subpod'][u'plaintext']
                if not res_found:
                    ismain = lambda d: u'@primary' in d.keys()
                    mainresult = filter(ismain, response[u'queryresult'][u'pod'])[0][u'subpod']
                    result = mainresult[u'plaintext'][u'#text']

                return u'{inter}: {res} -- {link}'.format(
                    inter = interpretation,
                    res = result,
                    link = url)
        except (socket.timeout, KeyError, TypeError, IndexError):
            return u'W|A dice {}'.format(url)
