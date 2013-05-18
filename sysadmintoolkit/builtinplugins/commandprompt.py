__version__ = '0.1.0a'

import sysadmintoolkit
import signal
import sys
import readline
import docutils.core
import tempfile


global plugin_instance

plugin_instance = None


def get_plugin(logger, config):
    '''
    '''
    global plugin_instance

    if plugin_instance is None:
        plugin_instance = CommandPrompt(logger, config)

    return plugin_instance


class CommandPrompt(sysadmintoolkit.plugin.Plugin):
    '''
    ====================
    CommandPrompt Plugin
    ====================

    Provides basic commands to the sysadmin-toolkit CLI.

    Configuration
    -------------

    *plugin-dir*
      Directory where plugins reside. Plugins must be with the .py extension.

      Default: /etc/sysadmin-toolkit/plugin.d/

    *script-dir*
      Directory where scripts reside. The commandprompt plugin doesn't do anything with this value.
      Other plugins would use it for indirection if needed.

      Default: /etc/sysadmin-toolkit/scripts.d/

    '''
    def __init__(self, logger, config):
        super(CommandPrompt, self).__init__('commandprompt', logger, config)

        self.add_command(sysadmintoolkit.command.LabelHelp('debug', self, 'Debug plugins'))
        self.add_command(sysadmintoolkit.command.ExecCommand('debug commandprompt', self, self.debug))

        # use_help = sysadmintoolkit.command.LabelHelp('use', self, 'Restrict the command to a specific plugin')
        # use_help._Label__is_reserved = True
        # self.add_command(use_help)

        # use_cmd = sysadmintoolkit.command.ExecCommand('use <plugin> <*>', self, self.cmd_input_with_scope)
        # use_cmd._Label__is_reserved = True
        # self.add_command(use_cmd)

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

        # set_cmd = sysadmintoolkit.command.ExecCommand('set', self, self.change_global_config)
        # set_cmd._Label__is_reserved = True
        # self.add_command(set_cmd)

        self.add_dynamic_keyword_fn('<plugin>', self.get_plugins)

        def sigint_handler(signum=None, frame=None):
            global plugin_instance
            plugin_instance.logger.info('Received signal %s' % signum)
            print '\n>> Use quit or exit to leave the program'
            sys.stdout.write('%s%s' % (plugin_instance.cmdstack[-1].prompt, readline.get_line_buffer()))
            sys.stdout.flush()

        signal.signal(signal.SIGINT, sigint_handler)

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
        print '  Loaded plugins: %s' % ', '.join(self.plugin_set.get_plugins().keys())
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

    # Dynamic keywords

    def get_plugins(self, dyn_keyword):
        plugins = self.plugin_set.get_plugins()

        map_plugins = {}

        for plugin in plugins:
            map_plugins[plugin] = 'Use %s plugin' % plugin

        return map_plugins

    # Sysadmin-toolkit commands

    def cmd_input_with_scope(self, line, mode):
        print 'cmd input with scope not implemented yet !!'

    def show_plugin_help(self, line, mode):
        if len(self.cmdstack):
            cmdprompt = self.cmdstack[-1]
        else:
            self.logger.error('This command must be executed interactively, please execute in the CLI')
            return

        pluginname = line.split()[1]
        plugin = self.plugin_set.get_plugins()[pluginname]

        self.logger.debug('Showing help for plugin %s' % pluginname)

        doc_file = tempfile.NamedTemporaryFile()

        plugin_doc = []

        plugin_doc.append(sysadmintoolkit.utils.trim_docstring(plugin.__doc__))
        plugin_doc.append('')

        labeldict = cmdprompt.command_tree.get_sub_keywords_labels()
        labelkeys = labeldict.keys()
        labelkeys.sort()

        plugin_command_doc = []
        for label in labelkeys:
            # Build the label part of the debug
            if len(labeldict[label]['executable_commands']) == 0:
                continue

            command_help_plugins = labeldict[label]['executable_commands'].keys()
            command_help_plugins.sort()

            for plugin in command_help_plugins:
                if plugin == pluginname:
                    plugin_command_doc.append('*%s*' % label.replace('_', ''))
                    command_help = labeldict[label]['executable_commands'][plugin].get_help()
                    plugin_command_doc.append(sysadmintoolkit.utils.indent_text(command_help, indent=2))

        self.logger.debug('Using merged docstrings for plugin %s:\n%s' % (pluginname, '\n'.join(plugin_doc + plugin_command_doc)))

        if len(plugin_command_doc):
            plugin_doc.append('Plugin Commands')
            plugin_doc.append('---------------')

        # Man page formatting
        manpage_format = docutils.core.publish_string('\n'.join(plugin_doc + plugin_command_doc), writer_name='manpage').splitlines()

        if '.SH NAME' in manpage_format[1]:
            manpage_format[1] = '.SH DESCRIPTION'

        if manpage_format[2].endswith('\\- '):
            manpage_format[2] = manpage_format[2][:-3]

        manpage_format = '\n'.join(manpage_format)

        doc_file.writelines('%s\n' % manpage_format)
        doc_file.flush()

        self.logger.debug('Using manpage for plugin %s:\n%s' % (pluginname, manpage_format))

        sysadmintoolkit.utils.execute_interactive_cmd('man %s' % doc_file.name, self.logger)

    def exit_last_commandprompt_level(self, line, mode):
        '''
        Exit the current command prompt
        '''
        return sysadmintoolkit.cmdprompt.EXIT_THIS_CMDPROMPT

    def exit_all_commandprompt_levels(self, line, mode):
        '''
        Exit the program
        '''
        return sysadmintoolkit.cmdprompt.EXIT_ALL_CMDPROMPT

    def change_global_config(self, line, mode):
        print 'change global config not implemented yet !!'
