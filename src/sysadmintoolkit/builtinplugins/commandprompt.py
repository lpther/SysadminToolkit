from sysadmintoolkit import plugin, command


class CommandPrompt(plugin.Plugin):
    '''
    '''
    def __init__(self, logger_):
        plugin.Plugin.__init__(self, "commandprompt", logger_)

        self.add_command(command.Command('debug commandprompt', self, self.debug))

    def debug(self, line, mode):
        print 'Commandprompt plugin printing some debug!'
