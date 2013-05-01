class SysadminToolkitError(Exception):
    '''
    Custom exception class
    '''
    def __init__(self, errmsg, errno=None):
        Exception.__init__(self)

        self.errno = errno
        self.errmsg = errmsg

        self.errdict = {}

    def __str__(self):
        return "%s: %s (error %s)" % (str(self.__class__).split("'")[1].split('.')[-1], self.errmsg, self.errno)


class CommandPromptError(SysadminToolkitError):
    '''
    '''
    def __init__(self, errmsg, errno=None, cmdprompt=None):
        SysadminToolkitError.__init__(self, errmsg, errno=errno)

        self.cmdprompt = cmdprompt

        self.errdict = {100: 'Alert', \
                        101: 'Could not create commandprompt', \
                        200: 'Critical', \
                        201: 'Could not instantiate plugin', \
                        300: 'Error', \
                        301: 'This is an unknown error in user input analysis', \
                        400: 'Warning', \
                        401: 'Plugin command returned exception', \
                        403: 'Command conflict detected', \
                        404: 'Label conflict detected', \
                        405: 'Dynamic keyword conflict', \
                        410: 'No executable command found at this label', \
                        411: 'Label had no match in registered commands', \
                        }


class PluginError(SysadminToolkitError):
    '''
    '''
    def __init__(self, errmsg, errno=None, plugin=None):
        SysadminToolkitError.__init__(self, errmsg, errno=errno)

        self.errdict = {200: 'Critical', \
                        300: 'Error', \
                        301: 'Error in registering command or plugin', \
                        302: 'Error in creating the plugin', \
                        303: 'Error in creating the comand', \
                        400: 'Warning', \
                        401: 'Could not add label to plugin', \
                        402: 'Could not add dynamic keyword to plugin', \
                        }

        self.plugin = plugin
