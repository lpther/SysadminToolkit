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
        from sysadmintoolkit import cmdprompt

        # Validate label
        try:
            self.label = cmdprompt.CmdPrompt.merge_keywords(cmdprompt.CmdPrompt.split_label(label))
        except:
            raise sysadmintoolkit.exception.PluginError('Error initializing command : Command instance requires a string (1st arg)', errno=303)

        # Validated Plugin
        if isinstance(plugin, sysadmintoolkit.plugin.Plugin):
            self.plugin = plugin
        else:
            raise sysadmintoolkit.exception.PluginError('Error initializing command : Command instance requires a Plugin instance (2nd arg) for label "%s"' % label, errno=303)

        for reserved_character in cmdprompt.CmdPrompt.get_reserved_characters():
            if reserved_character in label:
                raise sysadmintoolkit.exception.PluginError('Error initializing command : Invalid character in label "%s"' % label, errno=303)

    def get_label(self):
        '''
        '''
        return self.label

    def get_plugin(self):
        '''
        '''
        return self.plugin


class ExecCommand(Label):
    '''
    '''
    def __init__(self, label, plugin, function, allow_conflict=False):
        Label.__init__.__doc__ + \
        '''
        function     method   A method defined in the calling plugin.
                              def function(self, line, mode)
                              -> self will be plugin
                              -> Line entered at the cli, expanded
                              -> Command prompt Mode

        '''
        Label.__init__(self, label, plugin)

        # Validate function
        if type(function) is type(self.get_label):
            self.function = function
        else:
            raise sysadmintoolkit.exception.PluginError('Error initializing command : Command instance requires a function (3rd arg) for label "%s"' % label, errno=303)

    def get_function(self):
        '''
        '''
        return self.function


class _ReservedExecCommand(ExecCommand):
    ExecCommand.__doc__ + \
    '''
    Note: This label can only be registered by the plugin commandprompt
    '''

    def __init__(self, label, plugin, function, allow_conflict=False):
        ExecCommand.__init__.__doc__ + \
        '''
        '''
        ExecCommand.__init__(self, label, plugin, function, allow_conflict)


class LabelHelp(Label):
    '''
    '''

    def __init__(self, label, plugin, shorthelp):
        Label.__init__.__doc__ + \
        '''
        '''
        Label.__init__(self, label, plugin)

        self.shorthelp = shorthelp.strip().splitlines()[0]

    def get_shorthelp(self):
        '''
        '''
        return self.shorthelp


class _ReservedLabelHelp(LabelHelp):
    LabelHelp.__doc__ + \
    '''
    Note: This label can only be registered by the plugin commandprompt
    '''

    def __init__(self, label, plugin, shorthelp):
        LabelHelp.__init__.__doc__ + \
        '''
        '''
        LabelHelp.__init__(self, label, plugin, shorthelp)
