from sysadmintoolkit import plugin, command, utils


class CommandPrompt(plugin.Plugin):
    '''
    '''
    @classmethod
    def get_plugin(cls, config, logger):
        '''
        '''
        if CommandPrompt.plugin is None:
            CommandPrompt.plugin = CommandPrompt(logger, config)

        return CommandPrompt.plugin

    def __init__(self, logger, config):
        super(CommandPrompt, self).__init__("commandprompt", logger, config)

        self.add_command(command.LabelHelp('debug', self, 'Debug plugins'))
        self.add_command(command.ExecCommand('debug commandprompt', self, self.debug))

    def debug(self, line, mode):
        print 'Commandprompt plugin printing some debug!'

        if len(self.cmdstack):
            cmdprompt = self.cmdstack[-1]
        else:
            self.logger.error('This command must be executed interactively, please execute in the CLI')
            return

        width = utils.get_terminal_size()[1]

        sep = min(int(width * 0.66), 120)

        print
        print '  Command tree'
        print '  ============'
        print
        print '    Definitions: non executable, %s, %s' % (utils.get_underline_text('executable'), utils.get_reversed_text('<dynamic>'))
        print
        print '  %s %s' % ('Keyword'.ljust(sep), 'Help (plugin)')
        print '-' * len('  %s %s\n' % ('Keyword'.ljust(sep), 'Help (plugin)'))

        print cmdprompt.command_tree.get_sub_keywords_labels()
