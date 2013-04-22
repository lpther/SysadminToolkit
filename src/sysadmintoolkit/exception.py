class SysadminToolkitError(Exception):
    '''
    Custom exception class
    '''
    def __init__(self, errmsg, errno=None):
        Exception.__init__(self)

        self.errno = errno

        self.errdict = {}


class CommandPromptError(SysadminToolkitError):
    '''
    '''
    def __init__(self, errmsg, errno=None, cmdprompt=None):
        SysadminToolkitError.__init__(self, errmsg, errno=errno)

        self.cmdprompt = cmdprompt

        self.errdict = {100: 'Alert', \
                        101: 'Could not create commandprompt', \
                        200: 'Critical', \
                        201: 'Could not instanciate plugin', \
                        300: 'Error', \
                        400: 'Warning', \
                        }


class PluginError(SysadminToolkitError):
    '''
    '''
    def __init__(self, errmsg, errno=None, plugin=None):
        SysadminToolkitError.__init__(self, errmsg, errno=errno)

        self.errdict = {200: 'Critical', \
                        300: 'Error', \
                        301: 'Error in registering command', \
                        302: 'Error in creating the plugin', \
                        303: 'Error in creating the comand', \
                        400: 'Warning', \
                        }

        self.plugin = plugin
