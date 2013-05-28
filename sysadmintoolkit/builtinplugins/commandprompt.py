__version__ = '0.1.0b'

import sysadmintoolkit
import signal
import sys
import readline
import docutils.core
import tempfile
import collections


global plugin_instance

plugin_instance = None
modes_graph = collections.OrderedDict()
modes_graph['root'] = {'next_modes': ['config', 'operator'], 'desc': 'Display system properties, most commands require superuser privilege'}
modes_graph['config'] = {'next_modes': [], 'desc': 'Change system configuration'}
modes_graph['operator'] = {'next_modes': [], 'desc': 'View basic system properties'}


def get_plugin(logger, config):
    '''
    '''
    global plugin_instance, modes_graph

    if plugin_instance is None:
        plugin_instance = CommandPrompt(logger, config, modes_graph)

    return plugin_instance


class CommandPrompt(sysadmintoolkit.plugin.Plugin):
    '''
    Description
    -----------

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
    def __init__(self, logger, config, modes_graph):
        super(CommandPrompt, self).__init__('commandprompt', logger, config, version=__version__)

        self.modes_graph = modes_graph

        self.add_command(sysadmintoolkit.command.LabelHelp('debug', self, 'Debug plugins'))
        self.add_command(sysadmintoolkit.command.ExecCommand('debug commandprompt', self, self.debug))

        # use_help = sysadmintoolkit.command.LabelHelp('use', self, 'Restrict the command to a specific plugin')
        # use_help._Label__is_reserved = True
        # self.add_command(use_help)

        # use_cmd = sysadmintoolkit.command.ExecCommand('use <plugin> <*>', self, self.cmd_input_with_scope)
        # use_cmd._Label__is_reserved = True
        # self.add_command(use_cmd)

        switchmode_help = sysadmintoolkit.command.LabelHelp('switchmode', self, 'Change the command prompt mode')
        switchmode_help._Label__is_reserved = True
        self.add_command(switchmode_help)

        switchmode_cmd = sysadmintoolkit.command.ExecCommand('switchmode <mode>', self, self.change_mode)
        switchmode_cmd._Label__is_reserved = True
        self.add_command(switchmode_cmd)

        help_help = sysadmintoolkit.command.LabelHelp('help', self, 'Displays plugin help page')
        help_help._Label__is_reserved = True
        self.add_command(help_help)

        help_cmd = sysadmintoolkit.command.ExecCommand('help <plugin>', self, self.show_plugin_help)
        help_cmd._Label__is_reserved = True
        self.add_command(help_cmd)

        help_latex_cmd = sysadmintoolkit.command.ExecCommand('help <plugin> to-rst', self, self.show_plugin_help_rst)
        help_latex_cmd._Label__is_reserved = True
        self.add_command(help_latex_cmd)

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
        self.add_dynamic_keyword_fn('<mode>', self.get_modes)

        def sigint_handler(signum=None, frame=None):
            global plugin_instance
            plugin_instance.logger.info('Received signal %s' % signum)
            print '\n>> Use quit or exit to leave the program'
            sys.stdout.write('%s%s' % (plugin_instance.cmdstack[-1].prompt, readline.get_line_buffer()))
            sys.stdout.flush()

        signal.signal(signal.SIGINT, sigint_handler)

    def get_plugin_documentation(self, plugin):
        pluginname = plugin.get_name()

        plugin_doc_header = []

        plugin_doc_header.append(sysadmintoolkit.utils.trim_docstring(plugin.get_doc_header()))
        plugin_doc_header.append('')

        plugin_method_map = collections.OrderedDict()

        for mode in plugin.label_map:
            modename = mode

            if mode is '':
                modename = 'default'

            for label in plugin.label_map[mode]:
                command = plugin.label_map[mode][label]
                if not isinstance(command, sysadmintoolkit.command.ExecCommand):
                    continue

                method = command.get_function()

                if method not in plugin_method_map:
                    plugin_method_map[method] = {'longhelp': command.get_help(), 'shorthelp': command.get_shorthelp(), 'labels': {}}

                if label not in plugin_method_map[method]['labels']:
                    plugin_method_map[method]['labels'][label] = []

                plugin_method_map[method]['labels'][label].append(modename)
                plugin_method_map[method]['labels'][label].sort()

        plugin_command_doc = []

        plugin_method_map_keys = plugin_method_map.keys()
        for method in plugin_method_map_keys:
            method_dict = plugin_method_map[method]

            label_keys = method_dict['labels'].keys()
            label_keys.sort()

            plugin_command_doc.append('| ')

            for label in label_keys:
                plugin_command_doc.append('| *%s* (%s)' % (label, ', '.join(method_dict['labels'][label])))

                if label is label_keys[-1]:
                    plugin_command_doc.append('| ')

            plugin_command_doc.append('')

            plugin_command_doc.append(sysadmintoolkit.utils.indent_text(method_dict['longhelp'], indent=2))

            if method is not plugin_method_map_keys[-1]:
                plugin_command_doc.append('')
                plugin_command_doc.append('----')
                plugin_command_doc.append('')

        if len(plugin_command_doc):
            plugin_doc_header.append('Plugin Commands')
            plugin_doc_header.append('---------------')

        plugin_doc_footer = []
        plugin_doc_footer.append(plugin.get_doc_footer())
        plugin_doc_footer.append('')

        plugin_doc = '\n'.join(plugin_doc_header + plugin_command_doc + plugin_doc_footer)

        self.logger.debug('Using merged docstrings for plugin %s:\n%s' % (pluginname, plugin_doc))

        return plugin_doc

    # Dynamic keywords

    def get_plugins(self, user_input_obj):
        plugins = self.plugin_set.get_plugins()

        map_plugins = {}

        for plugin in plugins:
            map_plugins[plugin] = 'Use %s plugin' % plugin

        return map_plugins

    def get_modes(self, user_input_obj):
        current_mode = user_input_obj.get_mode()

        map_modes = {}

        for next_mode in self.modes_graph[current_mode]['next_modes']:
            map_modes[next_mode] = self.modes_graph[current_mode]['desc']

        return map_modes

    # Sysadmin-toolkit commands

    def debug(self, user_input_obj):
        '''
        Display registered commands in the current Command Prompt
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

        print '  Available modes'
        print '  ==============='
        print

        for mode in self.modes_graph:
            print '    %s %s' % (('%s:' % mode).ljust(20), self.modes_graph[mode]['desc'])
            print

            if len(self.modes_graph[mode]['next_modes']):
                print '    %s Next modes: %s' % (' ' * len(('%s:' % mode).ljust(20)), ', '.join(self.modes_graph[mode]['next_modes']))
            else:
                print '    %s Next modes: None' % (' ' * len(('%s:' % mode).ljust(20)))

            print

        print

    def show_plugin_help_rst(self, user_input_obj):
        '''
        Display man page for this plugin in reStructuredText format for documentation creation
        '''
        pluginname = user_input_obj.get_entered_command().split()[1]
        plugin = self.plugin_set.get_plugins()[pluginname]

        self.logger.debug('Showing rst documentation for plugin %s' % pluginname)

        print self.get_plugin_documentation(plugin)

    def show_plugin_help(self, user_input_obj):
        '''
        Display man page for this plugin

        '''
        pluginname = user_input_obj.get_entered_command().split()[1]
        plugin = self.plugin_set.get_plugins()[pluginname]

        self.logger.debug('Showing help for plugin %s' % pluginname)

        plugin_doc = self.get_plugin_documentation(plugin)

        plugin_doc_manpage_header = sysadmintoolkit.utils.trim_docstring("""
        %s=======
        %s Plugin
        %s=======
        """ % ('=' * len(pluginname), pluginname, '=' * len(pluginname)))

        self.logger.debug('Adding header for manpage:\n%s' % plugin_doc_manpage_header)

        doc_file = tempfile.NamedTemporaryFile()

        # Man page formatting
        manpage_format = docutils.core.publish_string('%s' % (plugin_doc), writer_name='manpage').splitlines()

        manpage_format[0] = '.TH %s COMMANDS "%s" "SYSADMIN-TOOLKIT PLUGIN" ""' % (plugin.get_name().upper(), plugin.get_version())

        if '.SH NAME' in manpage_format[1]:
            manpage_format[1] = ''

        if manpage_format[2].endswith('\\- '):
            manpage_format[2] = manpage_format[2][:-3]

        manpage_format = '\n'.join(manpage_format)

        doc_file.writelines('%s\n' % manpage_format)
        doc_file.flush()

        self.logger.debug('Using manpage for plugin %s:\n%s' % (pluginname, manpage_format))

        sysadmintoolkit.utils.execute_interactive_cmd('man %s' % doc_file.name, self.logger)

    def exit_last_commandprompt_level(self, user_input_obj):
        '''
        Exit the current command prompt

        '''
        return sysadmintoolkit.cmdprompt.EXIT_THIS_CMDPROMPT

    def exit_all_commandprompt_levels(self, user_input_obj):
        '''
        Exit the program

        '''
        return sysadmintoolkit.cmdprompt.EXIT_ALL_CMDPROMPT

    def change_mode(self, user_input_obj):
        '''
        Change the command prompt mode

        '''
        newmode = user_input_obj.get_entered_command().split()[-1]
        old_commandprompt = user_input_obj.get_cmdprompt()

        self.logger.debug('Changing mode from %s to %s' % (user_input_obj.get_mode(), newmode))

        newmode_commandprompt = sysadmintoolkit.cmdprompt.CmdPrompt(old_commandprompt.logger, mode=newmode, \
                                                         shell_allowed=old_commandprompt.shell_allowed, \
                                                         is_interactive=old_commandprompt.is_interactive)

        def SIGWINCH_handler(signum=None, frame=None):
            (height, width) = sysadmintoolkit.utils.get_terminal_size()
            newmode_commandprompt.update_window_size(width, height)

        old_sigwinch_handler = signal.signal(signal.SIGWINCH, SIGWINCH_handler)
        SIGWINCH_handler()

        for plugin in old_commandprompt.get_plugins():
            newmode_commandprompt.add_plugin(plugin)

        self.logger.debug('Entering cmdloop for command prompt in mode %s' % newmode)

        if old_commandprompt.is_interactive:
            newmode_commandprompt.cmdloop()
        else:
            newmode_commandprompt.preloop()
            return 0

        return_code = newmode_commandprompt.last_return_code

        if return_code is sysadmintoolkit.cmdprompt.EXIT_THIS_CMDPROMPT:
            self.logger.debug('Command prompt in mode %s exited' % newmode)
            return_code = 0
        elif return_code is sysadmintoolkit.cmdprompt.EXIT_ALL_CMDPROMPT:
            self.logger.debug('Command prompt in mode %s asked for a program exit' % newmode)
        else:
            self.logger.debug('Command prompt in mode %s exited with code %s' % (newmode, return_code))

        signal.signal(signal.SIGWINCH, old_sigwinch_handler)

        return return_code
