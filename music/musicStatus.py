#coding:utf8
from queryBot.responsemodule import IModule
import lastfmapi
import re

settings_name_g = u'music'
service_g       = u'service'
api_key_g       = u'api_key'

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
        return [('^\.np( (\S.*))?', self.now_playing)]

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
        if(self.settings[service_g] == 'lastfm' and \
           not self.settings[api_key_g] is None):
            self.api = lastfmapi.LastFmApi(self.settings[api_key_g])
        else:
            raise RuntimeError('Couldn\'t configure the module')

    def set_url_shortener(self, shortener):
        self.shorten_url = shortener.shorten_url

    # Functions that are needed for queries
    def now_playing(self, nick, message, channel):
        # check the message to see if we're being asked for a user different
        # from the user that sent the request
        query = re.sub(r'^\.np', '', message.decode('utf-8'), re.UNICODE).encode('utf-8')
        if query == u'':
            user = nick
        else:
            user = query.strip(u' \t\n\r')

        result = self.__fetch_status(user)

        if result and result != self.last_response:
            self.last_response = result
            return result.encode('utf-8', errors='ignore')

    def __fetch_status(self, luser):
        try:
            response = self.api.user_getRecentTracks(user=luser.encode('utf-8'))
        except lastfmapi.LastFmApiException:
            return u' '.join([luser, u'doesn\'t exist'])

        # if we later cannot find a song, we already know why:
        message = u' '.join([luser, u'isn\'t playing any song'])

        if u'track' in response[u'recenttracks'].keys() and len(response[u'recenttracks'][u'track']) > 0:
            rtrack = response[u'recenttracks'][u'track'][0]

            play_text = u'last played'
            time      = u''
            if u'@attr' in rtrack.keys() and u'nowplaying' in rtrack[u'@attr'].keys():
                play_text = u'is now playing'
            elif u'date' in rtrack.keys() and u'#text' in rtrack[u'date'].keys():
                time = u' on ' + rtrack[u'date'][u'#text']

            if u'name' in rtrack.keys() and \
                 u'artist' in rtrack.keys() and u'#text' in rtrack[u'artist'].keys():
                ltitle = rtrack[u'name']
                lartist = rtrack[u'artist'][u'#text']
            else:
                # we don't have title nor artist!!!
                return message

            loved    = u''
            tag_list = u''

            try:
                #fetch more info avout the track to display more info about it
                response = self.api.track_getInfo(track=ltitle.encode('utf-8'),
                                                  artist=lartist.encode('utf-8'),
                                                  username=luser.encode('utf-8'))

                # see if it's a 'loved' track
                if u'userloved' in response[u'track'].keys() and response[u'track'][u'userloved'] == '1':
                    loved = ' ♥'

                # add the tags of the track
                try:
                    toptags = response[u'track'][u'toptags'][u'tag']
                    tag_list = ' ('
                    for tag in toptags:
                        tag_list += tag[u'name'] + ', '
                    tag_list = tag_list[:-2] + ')'
                except Exception:
                    pass

            except lastfmapi.LastFmApiException:
                pass

            message = u'{user} {done}: {artist} — {song}{heart}{tags}{when}'.format(
                user   = luser,
                done   = play_text,
                song   = ltitle,
                artist = lartist,
                heart  = loved,
                tags   = tag_list,
                when   = time)

        return message