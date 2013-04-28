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

        self.add_command(command.LabelHelp('debug', self, 'Debug plugins'))
        self.add_command(command.ExecCommand('debug commandprompt', self, self.debug))

        use_help = command.LabelHelp('use', self, 'Restrict the command to a specific plugin')
        use_help._Label__is_reserved = True
        self.add_command(use_help)

        use_cmd = command.ExecCommand('use <pluginname> <*>', self, self.cmd_input_with_scope)
        use_cmd._Label__is_reserved = True
        self.add_command(use_cmd)

        help_help = command.LabelHelp('help', self, 'Displays plugin help page')
        help_help._Label__is_reserved = True
        self.add_command(help_help)

        help_cmd = command.ExecCommand('help <pluginname>', self, self.show_plugin_help)
        help_cmd._Label__is_reserved = True
        self.add_command(help_cmd)

    def debug(self, line, mode):
        '''
        Displays registered commands in the current Command Prompt
        '''
        if len(self.cmdstack):
            cmdprompt = self.cmdstack[-1]
        else:
            self.logger.error('This command must be executed interactively, please execute in the CLI')
            return

        width = utils.get_terminal_size()[1]

        window_ratio = 0.55
        max_block_size = 150
        first_block_len = min(width, int(max_block_size * window_ratio))
        second_block_len = min(width, int(max_block_size * (1 - window_ratio)))

        print
        print '  Command tree (%s)' % cmdprompt.mode
        print '  ' + ('=' * len('Command tree (%s)' % cmdprompt.mode))
        print
        print '    Definitions: non executable, %s, %s' % (utils.get_underline_text('executable'), utils.get_reversed_text('<dynamic>'))
        print
        print '  %s%s' % ('Keyword'.ljust(first_block_len - 1), 'Help (plugin)')
        print '-' * (first_block_len + second_block_len)

        labeldict = cmdprompt.command_tree.get_sub_keywords_labels()
        labelkeys = labeldict.keys()
        labelkeys.sort()

        for label in labelkeys:
            # Build the label part of the debug
            labelstr = ''
            for keyword in cmdprompt.split_label(label)[:-1]:
                if cmdprompt.is_dynamic_keyword(keyword):
                    keyword = utils.get_reversed_text(keyword)

                labelstr += utils.get_grey_text(keyword) + ' '

            lastkeyword = cmdprompt.split_label(label)[-1]

            if cmdprompt.is_dynamic_keyword(lastkeyword):
                lastkeyword = utils.get_reversed_text(lastkeyword)

            if len(labeldict[label]['executable_commands']) > 0:
                lastkeyword = utils.get_underline_text(lastkeyword)

            labelstr += lastkeyword

            label_text_block = ('  %s' % labelstr, window_ratio, max_block_size * window_ratio)
            blank_text_block = (' ', window_ratio, max_block_size * window_ratio)

            # Build the label help blocks
            label_help_blocks = []

            label_help_plugins = labeldict[label]['help'].keys()
            label_help_plugins.sort()

            for plugin in label_help_plugins:
                label_help_blocks += [('%s (%s)' % (labeldict[label]['help'][plugin].get_shorthelp(), plugin), \
                                       1 - window_ratio, max_block_size * (1 - window_ratio))]

            # Build the command help blocks
            command_help_blocks = []

            command_help_plugins = labeldict[label]['executable_commands'].keys()
            command_help_plugins.sort()

            for plugin in command_help_plugins:
                command_help_blocks += [('%s (%s)' % (labeldict[label]['executable_commands'][plugin].get_shorthelp(), \
                                                         plugin), 1 - window_ratio, max_block_size * (1 - window_ratio))]

            # Print all the gathered information
            output_so_far = False

            for right_block in label_help_blocks + command_help_blocks:
                if not output_so_far:
                    left_block = label_text_block
                    output_so_far = True
                else:
                    left_block = blank_text_block

                utils.print_text_blocks([left_block, right_block])

                print

        print

    def cmd_input_with_scope(self, line, mode):
        pass

    def show_plugin_help(self, line, mode):
        pass
