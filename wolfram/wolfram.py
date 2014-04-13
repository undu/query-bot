#encoding: utf-8
from queryBot.responsemodule import IModule
import urllib
import httplib2
import simplejson as json
from xml2json import xml2json
import re

class Wolfram(IModule):
    def __init__(self):
        self.settings = {u'api_key': None,
                         u'timeout': None}

        self.shorten_url = None
        self.last_response = u''

    def uses_settings(self):
        return True

    def get_command_patterns(self):
        return [('^\.(c|wa) (\S.*)', self.wolfAlpha)]

    def get_settings_name(self):
        return u'walpha'

    def get_configuration(self):
        return [(key, value) for (key, value) in self.settings.items() if not value is None]

    def set_configuration(self, settings):
        #fetch the settings
        for key, value in settings.items():
            if key in settings:
                self.settings[key] = value

        # signal when the module wasn't properly configured
        if(self.settings[u'api_key'] is None or self.settings[u'timeout']):
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
        ismain = lambda d: u'@primary' in d.keys()

        query = re.sub(r'^\.(c|wa)', u'', message.decode('utf-8'), re.UNICODE).encode('utf-8')
        query = query.strip(' \t\n\r')
        query = urllib.quote(query)
        queryurl = 'http://api.wolframalpha.com/v2/query?input=%s&appid=%s&format=plaintext&parsetimeout=0.5&formattimeout=0.5' %\
                   (query, self.walpha_api_key)
        shorturl = self.shorten_url(u'http://www.wolframalpha.com/input/?i=%s' %
                                    query)
        try:
            sock = httplib2.Http(timeout=self.walpha_timeout)
            headers, response = sock.request(queryurl)
        except socket.timeout:
            return u'W|A dice %s' % shorturl

        if headers['status'] in (200, '200'):
            #translate xml to json
            response = json.loads(xml2json(response, strip=0))
            try:
                interpretation = response['queryresult']['pod'][0]['subpod']['plaintext']['#text']
                mainresult = filter(ismain, response['queryresult']['pod'])[0]['subpod']
                result = mainresult['plaintext']['#text']

                interpretation
                result
                shorturl
                return u'%s: %s -- %s' % (interpretation, result, shorturl)
            except (KeyError, TypeError, IndexError):
                return u'W|A dice %s' % shorturl
