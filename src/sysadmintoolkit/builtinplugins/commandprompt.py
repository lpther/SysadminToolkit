from sysadmintoolkit import plugin, command, utils


class CommandPrompt(plugin.Plugin):
    '''
    '''
    def __init__(self, logger, config={}):
        plugin.Plugin.__init__(self, "commandprompt", logger, config)

        self.add_command(command.LabelHelp('debug', self, 'Debug plugins'))
        self.add_command(command.ExecCommand('debug commandprompt', self, self.debug))

    def debug(self, line, mode):
        print 'Commandprompt plugin printing some debug!'

        if len(self.cmdstack):
            cmdprompt = self.cmdstack[-1]
        else:
            self.logger.error('This command must be executed interactively, please execute in the CLI')
            return

        # printstr = ''

        (height, width) = utils.get_terminal_size()

        sep = min(int(width * 0.66), 120)

        header = ''
        header += '  Command tree\n'
        header += '  ============\n\n'
        header += '    Definitions: non executable, %s, %s\n\n' % (utils.get_underline_text('executable'), utils.get_reversed_text('dynamic'))
        header += '  %s %s\n' % ('Keyword'.ljust(sep), 'Help (plugin)')
        header += '-' * len('  %s %s\n' % ('Keyword'.ljust(sep), 'Help (plugin)'))

        utils.pager(header, height)

        print cmdprompt.command_tree.get_sub_keywords_labels()
