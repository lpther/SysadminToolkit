import sysadmintoolkit


class Label(object):
    '''
    '''

    def __init__(self, label, plugin):
        '''
        label        str      Full command label, keywords separated by spaces.
                              Special characters:
                                  <keyword>    indicates this is a dynamic keyword.
                                  *            indicates that the rest of the label will
                                               not be parsed and will be passed straight
                                               to the function
        plugin      Plugin   Plugin instance
        '''
        # Validate label
        try:
            self.label = sysadmintoolkit.cmdprompt.CmdPrompt.merge_keywords(sysadmintoolkit.cmdprompt.CmdPrompt.split_label(label))
        except:
            raise sysadmintoolkit.exception.PluginError('Error initializing command : Command instance requires a string (1st arg)', errno=303)

        # Validated Plugin
        if isinstance(plugin, sysadmintoolkit.plugin.Plugin):
            self.plugin = plugin
        else:
            raise sysadmintoolkit.exception.PluginError('Error initializing command : Command instance requires a Plugin instance (2nd arg) for label "%s"' % label, errno=303)

        for reserved_character in sysadmintoolkit.cmdprompt.CmdPrompt.get_reserved_characters():
            if reserved_character in label:
                raise sysadmintoolkit.exception.PluginError('Error initializing command : Invalid character in label "%s"' % label, errno=303)

        # Modify to your own risk.
        # Reserved commands affect how the commandprompt behaves
        self.__is_reserved = False

    def get_label(self):
        '''
        '''
        return self.label

    def get_plugin(self):
        '''
        '''
        return self.plugin

    def is_reserved(self):
        '''
        '''
        return self.__is_reserved


class ExecCommand(Label):
    '''
    '''

    def __init__(self, label, plugin, function, allow_conflict=False):
        '''
        function     method   A method defined in the calling plugin.
                              def function(self, line, mode)
                              -> self will be plugin
                              -> Line entered at the cli, expanded
                              -> Command prompt Mode

        '''
        super(ExecCommand, self).__init__(label, plugin)

        # Validate function
        if type(function) is type(self.get_label):
            self.function = function
        else:
            raise sysadmintoolkit.exception.PluginError('Error initializing command : Command instance requires a function (3rd arg) for label "%s"' % label, errno=303)

    def get_function(self):
        '''
        '''
        return self.function


class LabelHelp(Label):
    '''
    '''

    def __init__(self, label, plugin, shorthelp):
        '''
        '''
        super(LabelHelp, self).__init__(label, plugin)

        self.shorthelp = shorthelp.strip().splitlines()[0]

    def get_shorthelp(self):
        '''
        '''
        return self.shorthelp
