#coding:utf8
from queryBot.responsemodule import IModule
import lastfmapi

api_key_g = 'api_key'
service_g = 'service'

class MusicStatus(IModule):
    def __init__(self):
        self.settings = {api_key_g: None,
                         service_g: None}

        self.api = None
        self.shorten_url = None
        self.last_response = u''

    def uses_settings(self):
        return True

    def get_command_patterns(self):
        return [('^\.np (\S.*)', self.now_playing)]

    def get_settings_name(self):
        return 'music'

    def get_configuration(self):
        return [(key, value) for (key, value) in self.settings.items() if not value is None]

    def set_configuration(self, settings):
        #fetch the settings
        for key, value in settings.items():
            if key in settings:
                self.settings[key] = value

        # now we can configure the module
        if(self.settings[service_g] == 'lastfm' and \
           not self.settings[api_key_g] is None):
            self.api = lastfmapi.LastFmApi(self.settings[api_key_g])
        else:
            raise RuntimeError('Couldn\'t configure the module')

    def set_url_shortener(self, shortener):
        self.shorten_url = shortener.shorten_url

    # Functions that are needed for queries
    def now_playing(self, nick, message, channel):
        result = self.fetch_status(nick)
        #raise NotImplementedError()
        if result and result != self.last_response:
            self.last_response = result
            return result.encode('utf-8', errors='ignore')

    def __fetch_status(self, luser):
        #cleanup the message to get the query
        #query = re.sub(r'^\.np', '', message.decode('utf-8'), re.UNICODE).encode('utf-8')
        #luser = query.strip(u' \t\n\r')
        try:
            response = self.api.user_getRecentTracks(user=luser.encode('utf-8'))
        except lastfmapi.LastFmApiException:
            return u' '.join([luser, u'doesn\'t exist'])
        message = u' '.join([luser, u'isn\'t playing any song'])

        if u'track' in response[u'recenttracks'].keys() and len(response[u'recenttracks'][u'track']) > 0:
            rtrack = response[u'recenttracks'][u'track'][0]
            if u'@attr' in rtrack.keys() and u'nowplaying' in rtrack['@attr'].keys():
                ltitle = rtrack[u'name']
                lartist = rtrack[u'artist'][u'#text']

                message = u' '.join([luser,  u'is now playing', ltitle, u'—',  lartist])

            try:
                response = self.api.track_getInfo(track=ltitle.encode('utf-8'),artist=lartist.encode('utf-8'),username=luser.encode('utf-8'))
            except lastfmapi.LastFmApiException:
                return message

            if u'userloved' in response[u'track'].keys() and response[u'track'][u'userloved'] == '1':
                message += ' ♥'
            try:
                toptags = response[u'track'][u'toptags'][u'tag']
                message += ' ('
                for tag in toptags:
                    message += tag[u'name'] + ', '
                message = message[:-2] + ')'
            except Exception:
                pass

        return message