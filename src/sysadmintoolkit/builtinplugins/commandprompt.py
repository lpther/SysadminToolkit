from sysadmintoolkit import plugin, command, utils

global plugin_instance

plugin_instance = None


def get_plugin(config, logger):
    '''
    '''
    global plugin_instance

    if plugin_instance is None:
        plugin_instance = CommandPrompt(logger, config)

    return plugin_instance


class CommandPrompt(plugin.Plugin):
    '''
    '''
    def __init__(self, logger, config):
        super(CommandPrompt, self).__init__("commandprompt", logger, config)

        debug_help = command.LabelHelp('debug', self, 'Debug plugins')
        debug_help.__Label__is_reserved = True
        self.add_command(debug_help)

        debug_commandprompt = command.ExecCommand('debug commandprompt', self, self.debug)
        debug_commandprompt.__Label__is_reserved = True
        self.add_command(debug_commandprompt)

        self.add_command(command.ExecCommand('dtest debug commandprompt', self, self.debug))
        self.add_command(command.ExecCommand('dtesting debug commandprompt', self, self.debug))

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
