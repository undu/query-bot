#encoding: utf-8
from responsemodule import IModule
import bitly_api

''' Example config:
[url_short]
service=bitly
user=username
api_key=R_12345678901234567890123456789012
'''
settings_name_g = u'url_short'
api_key_g       = u'api_key'
user_g          = u'user'
service_g       = u'service'

class Shortener(IModule):
    def __init__(self):
        self.settings = {api_key_g: None,
                         user_g:    None,
                         service_g: None}
        self.engine = None

    def uses_settings(self):
        return True

    def get_command_patterns(self):
        return []

    def get_settings_name(self):
        return settings_name_g

    def get_configuration(self):
        return [(key, value) for (key, value) in self.settings.items() if not value is None]

    def set_configuration(self, settings):
        #fetch the settings
        for key, value in settings.items():
            if key in settings:
                self.settings[key] = value
        # now we can configure the module
        if(self.settings[service_g] == u'bitly' and \
           not (self.settings[user_g] is None or \
                self.settings[api_key_g] is None)):
            self.engine = bitly_api.Connection(self.settings[user_g], self.settings[api_key_g])
        else:
            raise RuntimeError('Couldn\'t configure the module')

    def set_url_shortener(self, shorten_url):
        pass

    def shorten_url(self, url):
        data = self.engine.shorten(url)
        if data is None:
            short_url = url
        else:
            short_url = data['url']
        return short_url

    def __str__(self):
        if self.engine is None:
            return "URL Shortener"
        else:
            return "{user}'s {service} shortener".format(
                user = self.settings[user_g],
                service = self.settings[service_g])