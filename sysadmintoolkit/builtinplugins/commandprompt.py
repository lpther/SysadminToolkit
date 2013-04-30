import sysadmintoolkit

global plugin_instance

plugin_instance = None


def get_plugin(config, logger):
    '''
    '''
    global plugin_instance

    if plugin_instance is None:
        plugin_instance = CommandPrompt(logger, config)

    return plugin_instance


class CommandPrompt(sysadmintoolkit.plugin.Plugin):
    '''
    '''
    def __init__(self, logger, config):
        super(CommandPrompt, self).__init__("commandprompt", logger, config)

        self.add_command(sysadmintoolkit.command.LabelHelp('debug', self, 'Debug plugins'))
        self.add_command(sysadmintoolkit.command.ExecCommand('debug commandprompt', self, self.debug))

        use_help = sysadmintoolkit.command.LabelHelp('use', self, 'Restrict the command to a specific plugin')
        use_help._Label__is_reserved = True
        self.add_command(use_help)

        use_cmd = sysadmintoolkit.command.ExecCommand('use <plugin> <*>', self, self.cmd_input_with_scope)
        use_cmd._Label__is_reserved = True
        self.add_command(use_cmd)

        help_help = sysadmintoolkit.command.LabelHelp('help', self, 'Displays plugin help page')
        help_help._Label__is_reserved = True
        self.add_command(help_help)

        help_cmd = sysadmintoolkit.command.ExecCommand('help <plugin>', self, self.show_plugin_help)
        help_cmd._Label__is_reserved = True
        self.add_command(help_cmd)

        exit_cmd = sysadmintoolkit.command.ExecCommand('exit', self, self.exit_last_commandprompt_level)
        exit_cmd._Label__is_reserved = True
        self.add_command(exit_cmd)

        quit_cmd = sysadmintoolkit.command.ExecCommand('quit', self, self.exit_all_commandprompt_levels)
        quit_cmd._Label__is_reserved = True
        self.add_command(quit_cmd)

        set_cmd = sysadmintoolkit.command.ExecCommand('set', self, self.change_global_config)
        set_cmd._Label__is_reserved = True
        self.add_command(set_cmd)

        self.add_dynamic_keyword_fn('<plugin>', self.get_plugins_for_use_cmd)

    def debug(self, line, mode):
        '''
        Displays registered commands in the current Command Prompt
        '''
        if len(self.cmdstack):
            cmdprompt = self.cmdstack[-1]
        else:
            self.logger.error('This command must be executed interactively, please execute in the CLI')
            return

        width = sysadmintoolkit.utils.get_terminal_size()[1]

        window_ratio = 0.55
        max_block_size = 150
        first_block_len = int(min(width, max_block_size) * window_ratio) - 1
        second_block_len = int(min(width, max_block_size) * (1 - window_ratio)) - 1

        print
        print '  Command tree (%s)' % cmdprompt.mode
        print '  ' + ('=' * len('Command tree (%s)' % cmdprompt.mode))
        print
        print '    Definitions: non executable, %s, %s' % (sysadmintoolkit.utils.get_underline_text('executable'), \
                                                           sysadmintoolkit.utils.get_reversed_text('<dynamic>'))
        print
        print '  %s%s' % ('Keyword'.ljust(first_block_len), 'Help (plugin)')
        print '-' * (first_block_len + second_block_len)

        labeldict = cmdprompt.command_tree.get_sub_keywords_labels()
        labelkeys = labeldict.keys()
        labelkeys.sort()

        for label in labelkeys:
            # Build the label part of the debug
            labelstr = ''
            for keyword in cmdprompt.split_label(label)[:-1]:
                if cmdprompt.is_dynamic_keyword(keyword):
                    keyword = sysadmintoolkit.utils.get_reversed_text(keyword)

                labelstr += sysadmintoolkit.utils.get_grey_text(keyword) + ' '

            lastkeyword = cmdprompt.split_label(label)[-1]

            if cmdprompt.is_dynamic_keyword(lastkeyword):
                lastkeyword = sysadmintoolkit.utils.get_reversed_text(lastkeyword)

            if len(labeldict[label]['executable_commands']) > 0:
                lastkeyword = sysadmintoolkit.utils.get_underline_text(lastkeyword)

            labelstr += lastkeyword

            label_text_block = {'str': '%s' % labelstr, 'window_ratio': window_ratio, 'maxwidth': max_block_size * window_ratio, 'wrap': False}
            blank_text_block = {'str': ' ', 'window_ratio': window_ratio, 'maxwidth': max_block_size * window_ratio, 'wrap': True}

            # Build the label help blocks
            label_help_blocks = []

            label_help_plugins = labeldict[label]['help'].keys()
            label_help_plugins.sort()

            for plugin in label_help_plugins:
                label_help_blocks += [{'str':'%s (%s)' % (labeldict[label]['help'][plugin].get_shorthelp(), plugin), \
                                       'window_ratio': 1 - window_ratio, \
                                       'maxwidth': max_block_size * (1 - window_ratio), \
                                       'wrap': True
                                       }]

            # Build the command help blocks
            command_help_blocks = []

            command_help_plugins = labeldict[label]['executable_commands'].keys()
            command_help_plugins.sort()

            for plugin in command_help_plugins:
                command_help_blocks += [{'str': '%s (%s)' % (labeldict[label]['executable_commands'][plugin].get_shorthelp(), plugin), \
                                         'window_ratio': 1 - window_ratio, \
                                         'maxwidth': max_block_size * (1 - window_ratio), \
                                         'wrap': True
                                         }]

            # Print all the gathered information
            output_so_far = False

            for right_block in label_help_blocks + command_help_blocks:
                if not output_so_far:
                    left_block = label_text_block
                    output_so_far = True
                else:
                    left_block = blank_text_block

                sysadmintoolkit.utils.print_text_blocks([left_block, right_block])

                print

        print

    def get_plugins_for_use_cmd(self, dyn_keyword):
        plugins = self.cmdstack[-1].get_plugins()

        map_dyn_keyword = {}

        for plugin in plugins:
            map_dyn_keyword[plugin.get_name()] = 'Restrict the scope to %s plugin' % plugin.get_name()

        return map_dyn_keyword

    def cmd_input_with_scope(self, line, mode):
        print 'cmd input with scope not implemented yet !!'

    def show_plugin_help(self, line, mode):
        print 'show plugin help not implemented yet !!'

    def exit_last_commandprompt_level(self, line, mode):
        print 'exit last command prompt level not implemented yet !!'

    def exit_all_commandprompt_levels(self, line, mode):
        print 'exit all command prompts not implemented yet !!'

    def change_global_config(self, line, mode):
        print 'change global config not implemented yet !!'
        raise sysadmintoolkit.exception.CommandPromptError('Error initializing plugin : Plugin name requires a string (1st arg)', errno=302)
