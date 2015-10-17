#coding:utf-8
from responsemodule import IModule
import re
import urllib
import HTMLParser
import httplib2
import simplejson as json

class GoogleSearch(IModule):

    def __init__(self):
        self.last_response = u''
        self.shorten_url = None

    def uses_settings(self):
        return False

    def get_command_patterns(self):
        return [('^\.g (\S.*)', self.google)]

    def get_settings_name(self):
        return u'google'

    def get_configuration(self):
        return None

    def set_configuration(self, settings):
        pass

    def set_url_shortener(self, shortener):
        self.shorten_url = shortener.shorten_url

    # Functions that are needed for queries
    def google(self, nick, message, channel):
        result = self.__fetch_google(message)
        if result and result != self.last_response:
            self.last_response = result
            return result.encode('utf-8', errors='ignore')

    def __fetch_google(self, message):
        # COnverts a number representation to character
        char = lambda matchobj: chr(int(matchobj.group('n')))

        # Clean up the message to isolate the query and make it url-safe
        query = re.sub(r'^\.g', u'', message.decode('utf-8'), re.UNICODE).encode('utf-8')
        query = query.strip()
        query = urllib.quote(query)
        query_url = 'http://ajax.googleapis.com/ajax/services/search/web?v=2.0&q=%s' % \
                    query


        body = u''
        url = url = u'http://www.google.com/?q=%s' % query

        try:
            # Query google
            sock = httplib2.Http(timeout=1)
            headers, response = sock.request(query_url)

            # Check result and clean it up for displaying
            if headers['status'] in (200, '200'):
                response = json.loads(response)
                if response['responseStatus'] != 403:
                    try:
                        url     = response['responseData']['results'][0]['unescapedUrl']
                        title   = response['responseData']['results'][0]['titleNoFormatting']
                        content = response['responseData']['results'][0]['content']

                        # Convert HTML-encoded characters to sane encoding
                        content = HTMLParser.HTMLParser().unescape(content)
                        content = re.sub(r'&#(?P<n>[0-9]+);', char, content, re.UNICODE)
                        content = re.sub(r'<[^>]+>', '', content)
                        content = re.sub(r'\s+', ' ', content)

                        title   = HTMLParser.HTMLParser().unescape(title)
                        title   = re.sub(r'&#(?P<n>[0-9]+);', char, title, re.UNICODE)
                        title   = re.sub(r'<[^>]+>', '', title, re.UNICODE)
                        title   = re.sub(r'\s+', '', title, re.UNICODE)

                        body = u'%s: %s -- ' % (title, content)

                    except (IndexError, TypeError):
                        url = response[u'responseData'][u'cursor'][u'moreResultsUrl']
                        body = u''

                # shorten the url if available and construct the final message
                if(self.shorten_url is None):
                    url = url.decode('utf-8', errors='ignore')
                else:
                    url = self.shorten_url(url).decode('utf-8', errors='ignore')

        finally:
            return body + url
