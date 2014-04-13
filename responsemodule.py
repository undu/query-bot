class IModule(object):
    """ Returns if the module needs settings to work or not.
    """
    def uses_settings(self):
        raise NotImplementedError('')

    """ Returns a list of tuples. Each tuple contains a regular expression
        and a callback function.
        The regex is used to decide when is the callback going to be called.
        The callback function has the signature (self, nick, message,
        channel), all of them strings.
    """
    def get_command_patterns(self):
        raise NotImplementedError('')

    """ Returns the name of the section in the setting that the module uses
        for configuration
    """
    def get_settings_name(self):
        raise NotImplementedError('')

    """ Return the current settings as a list of tuples
    """
    def get_configuration(self):
        raise NotImplementedError('')

    """ Makes the module load the settings so it can work correctly
        settings is a dict.
    """
    def set_configuration(self, settings):
        raise NotImplementedError('')

    """ Sends the class that'll write the settings for the module to
        use the callback.
    """
    def set_configuration_writer(self, write_f):
        raise NotImplementedError('')
