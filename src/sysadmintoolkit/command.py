from sysadmintoolkit import exception, plugin


class Command(object):
    '''
    '''

    def __init__(self, label, plugin_, function):
        '''
        '''
        from sysadmintoolkit import cmdprompt

        # Validate label
        try:
            self.label = cmdprompt.merge_keywords(cmdprompt.split_label(label))
        except:
            raise exception.PluginError('Error initializing command : Command instance requires a string (1st arg)', errno=303)

        # Validated Plugin
        if isinstance(plugin_, plugin.Plugin):
            self.plugin = plugin_
        else:
            raise exception.PluginError('Error initializing command : Command instance requires a Plugin instance (2nd arg) for label "%s"' % label, errno=303)

        # Validate function
        if type(function) is type(self.get_label):
            self.function = function
        else:
            raise exception.PluginError('Error initializing command : Command instance requires a function (3rd arg) for label "%s"' % label, errno=303)

    def get_label(self):
        '''
        '''
        return self.label

    def get_plugin(self):
        '''
        '''
        return self.plugin

    def get_function(self):
        '''
        '''
        return self.function
