#encoding: utf-8
from irc import IRCBot
from google.googleSearch import GoogleSearch
from music.musicStatus import MusicStatus
from urlshortener.shortener import Shortener
#from wolfram.wolfram import Wolfram
from ConfigParser import SafeConfigParser
import random
import codecs

config_name_g = u'config'

class QueryBot(IRCBot):
    def __init__(self, *args, **kwargs):
        # enable by default modules that don't require configuration, do it before the innit
        # of the super class because otherwise it tries to register the callbacks and crashes
        # when the list is not defined
        shortener = Shortener()
        modules = [shortener, GoogleSearch(), MusicStatus()]#, Wolfram()]
        self.enabled_modules = [module for module in modules if not module.uses_settings()]

        #last response given, to avoid spam
        self.last_response = u''

        conf = False
        if(config_name_g in kwargs):
            parser = SafeConfigParser()
            with codecs.open(kwargs[config_name_g], 'r', encoding='utf-8') as f:
                parser.readfp(f)
            if parser.sections() != []:
                conf = True

        #log "configuration file has " + "been loaded" if conf else "not been loaded"
        if conf:
            #fit all the configuration into a {str: {str: str}}
            configs = dict([(module, {option: value for (option, value) in parser.items(module)})
                        for module in parser.sections()])
            #enable only the modules which get configured properly
            get_conf_name = lambda m: (m, m.get_settings_name())
            for module, name in map(get_conf_name, modules):
                if name in configs:
                    try:

                        module.set_configuration(configs[name])
                        self.enabled_modules.append(module)
                    except RuntimeError:
                        print ('Couldn\'t load configuration for module "' + str(module)) + '"'

        # now that we have decided what modules can function let's finish configuring them
        if(shortener in self.enabled_modules):
            for module in self.enabled_modules:
                module.set_url_shortener(shortener)

        # essential to do now because we have now the enabled modules
        super(QueryBot, self).__init__(*args, **kwargs)

    def command_patterns(self):
        return [com_pat for module in self.enabled_modules for com_pat in module.get_command_patterns()] + [
            ('(?i)^f+$', self._fuckYou),
            ('^\.h(elp)?', self._help)
        ]

    def _fuckYou(self, nick, message, channel):
        response = u'Fuck you, %s' % nick
        if random.random() < 0.4 and response != self.last_response:
            return response.encode('utf-8', errors='ignore')

    def _help(self, nick, message, channel):
        result = 'Comandos disponibles: google: ".g <busqueda>" --- conversor/calculadora: ".c <operacion>" --- wolfram|alpha: ".wa <pregunta>"'
        if result != self.last_response:
            self.last_response = result
            return result.encode('utf-8', errors='ignore')
