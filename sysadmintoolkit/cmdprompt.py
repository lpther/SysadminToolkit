import sysadmintoolkit
import cmd
import readline
import logging
import pprint


class CmdPrompt(cmd.Cmd):
    '''
    '''
    @classmethod
    def split_label(cls, label, first_keyword_only=False, preserve_spaces=False):
        '''
        Returns a list of keywords from the label

        first_keyword_only    bool      Only the first keyword is poped, the rest of
                                        the list is the rest of the label unchanged
        preserve_spaces       bool      Do not remove trailing spaces for the returned keyword list
                                        (to help printing)
        '''
        if isinstance(label, str):
            if label is '':
                if first_keyword_only:
                    return ['', '']
                else:
                    return ['']

            if first_keyword_only:
                first_keyword = label.split()[0]

                rest_of_label = label.split(' ')
                rest_of_label.remove(first_keyword)

                return [first_keyword, ' '.join(rest_of_label).strip()]
            else:
                if not preserve_spaces:
                    return label.split()
                else:
                    keywords = []
                    current_keyword = label.split(' ')[0]
                    for token in label.split(' ')[1:]:
                        if token is '':
                            current_keyword += ' '
                        else:
                            keywords += [current_keyword]
                            current_keyword = token

                    return keywords

        else:
            raise sysadmintoolkit.exception.SysadminToolkitError('Label is not string type')

    @classmethod
    def merge_keywords(cls, keywords):
        '''Returns a label from the list of keywords
        '''
        if isinstance(keywords, list):
            for item in keywords:
                if not isinstance(item, str):
                    raise sysadmintoolkit.exception.SysadminToolkitError('Keyword is not str type')

            if '' in keywords:
                keywords.remove('')

            return ' '.join(keywords)
        else:
            raise sysadmintoolkit.exception.SysadminToolkitError('Keywords is not list type')

    @classmethod
    def get_reserved_characters(cls):
        '''
        '''
        return ['\n', '\r', '?', '|', '!']

    @classmethod
    def is_dynamic_keyword(cls, keyword):
        return keyword.startswith('<') and keyword.endswith('>')

    def __init__(self, logger, completekey='tab', stdin=None, stdout=None,
                 mode="generic", prompt='sysadmin-toolkit# ',
                 shell_allowed=False, is_interactive=True):
        '''
        '''
        cmd.Cmd.__init__(self, completekey='tab', stdin=None, stdout=None)

        if isinstance(logger, logging.Logger):
            self.logger = logger
        else:
            raise sysadmintoolkit.exception.CommandPromptError('Could not initialize command prompt: Wrong logger class', errno=101)

        if isinstance(mode, str):
            self.mode = mode
        else:
            raise sysadmintoolkit.exception.CommandPromptError('Could not initialize command prompt: Mode should be a string', errno=101)

        self.logger.debug('New command prompt in mode %s ' % mode)

        # Switching readline delims for allowed characters
        readline.set_completer_delims(' \n\r')

        self.logger.debug('  raw readline completer delims="%s"' % readline.get_completer_delims().__repr__())
        self.logger.debug('  identchars="%s"' % self.identchars)

        # Root of the command tree
        self.command_tree = sysadmintoolkit.keyword._Keyword(logger)

        # List of registered plugins
        self.plugins = []

        # Global help is removed from Cmd class and handled in this subclass
        try:
            del cmd.Cmd.do_help
            del cmd.Cmd.complete_help
        except:
            pass

        self.shell_allowed = shell_allowed

        self.prompt = prompt

        self.is_interactive = is_interactive

    def add_plugin(self, plugin):
        '''Adds the plugin to cmdprompt, and registers the plugin's label to the cmdprompt
        '''
        if not isinstance(plugin, sysadmintoolkit.plugin.Plugin):
            raise sysadmintoolkit.exception.PluginError('Error initializing Command Prompt: add_plugin requires Plugin class ', errno=301)

        if plugin not in self.plugins:
            self.plugins += [plugin]
        else:
            raise sysadmintoolkit.exception.PluginError('Error initializing Command Prompt: plugin already registered ', errno=301)

        self.logger.debug('Adding plugin %s in mode %s' % (plugin.get_name(), self.mode))

        # Add plugin's commands for current mode
        for command in plugin.get_commands(self.mode):
            self.register_command(command, CmdPrompt.split_label(command.get_label()))

        for command in plugin.get_commands(''):
            self.register_command(command)

    def get_plugins(self):
        return self.plugins

    def register_command(self, command):
        '''
        '''
        if not isinstance(command, sysadmintoolkit.command.Label):
            raise sysadmintoolkit.exception.PluginError('Error initializing Command Prompt: register_command requires Command class ', errno=301)

        self.logger.debug('Registering command label "%s" into command tree' % (command.get_label()))

        self.command_tree.add_command(CmdPrompt.split_label(command.get_label()), command)

    # Redefining commands from cmd.CMD

    def default(self, line, plugin_scope=None):
        """
        Handle command line input and take appropriate action
        """
        self.logger.debug("Command Prompt: default: line='%s'" % (line))
        self.logger.debug("  lastcmd='%s'" % (self.lastcmd))
        self.logger.debug("  readlinebuff='%s'" % (readline.get_line_buffer()))
        self.logger.debug("  plugin_scope='%s'" % (plugin_scope))

        statusdict = self.get_line_status(line, plugin_scope)

        if statusdict['status'] is 'exec_commands':
            # The command matches to a label in the keyword tree
            # Action: Execute the command (if allowed by the commands)
            executable_commands = statusdict['keyword_tree'].get_executable_commands()

            keys = executable_commands.keys()
            keys.sort()

            for keycmd in keys:
                if len(keys) > 0:
                    print '** Executing command from %s **' % executable_commands[keycmd].get_plugin().get_name()

                try:
                    return_code = executable_commands[keycmd].get_function()(line, self.mode)

                    if not self.is_interactive:
                        return return_code
                    else:
                        return

                except Exception as e:
                    self.logger.error('Error executing label %s with plugin %s in mode %s:\n%s' % \
                                 (statusdict['expanded_label'], executable_commands[keycmd].get_plugin().get_name(), self.mode, str(e)))

                    print '>> Error in command execution (see logs for details) : %s' % str(e).split()[0]

                    if not self.is_interactive:
                        return 401
                    else:
                        return

        elif statusdict['status'] is 'command_conflict':
            # One or more commands are executable, but they do not allow conflict
            # Action: Display error message
            ok_keywords = ''.join(self.split_label(line, preserve_spaces=True)[:statusdict['keyword_pos'] - 1])
            leading_whitespaces = len(line) - len(line.lstrip())

            self.print_cli_error(len(self.prompt + ok_keywords) + leading_whitespaces, 'Command conflict detected, type "use <plugin> cmd" to specigy plugin !')

            if not self.is_interactive:
                return 403
            else:
                return

        elif statusdict['status'] is 'no_command_match':
            # There is a matching label but no matching executable command
            # Action: Display error message for the keyword
            ok_keywords = ''.join(self.split_label(line, preserve_spaces=True)[:statusdict['keyword_pos'] - 1])
            leading_whitespaces = len(line) - len(line.lstrip())

            if plugin_scope is None:
                self.print_cli_error(len(self.prompt + ok_keywords) + leading_whitespaces, 'No executable command found !')
            else:
                self.print_cli_error(len(self.prompt + ok_keywords) + leading_whitespaces, 'No executable command found for plugin %s !' % plugin_scope)

            if not self.is_interactive:
                return 402
            else:
                return

        elif statusdict['status'] is 'no_label_match':
            # There is no matching label in the keyword tree,
            # Action: Display error message for the bad keyword
            ok_keywords = ''.join(self.split_label(line, preserve_spaces=True)[:statusdict['keyword_pos'] - 1])
            leading_whitespaces = len(line) - len(line.lstrip())

            self.print_cli_error(len(self.prompt + ok_keywords) + leading_whitespaces, 'No matching command found !')

            if not self.is_interactive:
                return 402
            else:
                return

        elif statusdict['status'] is 'label_conflict':
            # More than one label matches the keyword
            # Action: Display error message about the conflicting keyword
            ok_keywords = ''.join(self.split_label(line, preserve_spaces=True)[:statusdict['keyword_pos'] - 1])
            leading_whitespaces = len(line) - len(line.lstrip())

            self.print_cli_error(len(self.prompt + ok_keywords) + leading_whitespaces, 'Conflict found! Either type "use <plugin> cmd" or type the complete command')

            # The conflict is not at the end of the command
            # Action: Display conflicting keywords and their related plugins
            self.print_conflict_keywords(statusdict)

            if not self.is_interactive:
                return 403
            else:
                return

        return

    def complete_default(self, text, line, begidx, endidx):
        '''
        '''
        self.logger.debug("Command Prompt: completedefault: text='%s' line='%s' begidx=%s endidx=%s" % (text, line, begidx, endidx))
        self.logger.debug("  lastcmd='%s'" % (self.lastcmd))
        self.logger.debug("  readlinebuff='%s'" % (readline.get_line_buffer()))

        return []

    def complete(self, text, state):
        '''
        '''
        self.logger.debug("\nCommand Prompt: complete: text='%s' state=%s" % (text, state))
        self.logger.debug("  completiontype=%s" % (readline.get_completion_type()))
        self.logger.debug("  lastcmd='%s'" % (self.lastcmd))
        self.logger.debug("  readlinebuff='%s'" % (readline.get_line_buffer()))

    def get_line_status(self, line, plugin_scope=None):
        '''
        Analyze the user input and return the status

        pluginscope        str        Restrict matches to this module
        '''
        self.logger.debug('Line analysis started for line "%s" in mode %s (scope is %s)' % (line, self.mode, plugin_scope))
        pp = pprint.PrettyPrinter(indent=2)

        statusdict = {'expanded_label': '',
                      'plugin_scope': plugin_scope}

        keyword_tree = self.command_tree
        rest_of_line = line
        keyword_pos = 1

        while True:
            [this_keyword, rest_of_line] = self.split_label(rest_of_line, first_keyword_only=True)

            possible_keywords = keyword_tree.get_sub_keywords_keys()

            matching_keywords = sysadmintoolkit.utils.get_matching_prefix(this_keyword, possible_keywords)

            self.logger.debug('-' * 50)
            self.logger.debug('this_keyword="%s" rest_of_line="%s"' % (this_keyword, rest_of_line))
            self.logger.debug('possible_keywords=%s' % possible_keywords)
            self.logger.debug('matching_keywords="%s"' % matching_keywords)

            statusdict['keyword'] = this_keyword
            statusdict['keyword_tree'] = keyword_tree
            statusdict['keyword_pos'] = keyword_pos
            statusdict['matching_keywords'] = matching_keywords
            statusdict['rest_of_line'] = rest_of_line
            statusdict['commands'] = []

            if this_keyword is '':
                # End of user input for this label
                statusdict['keyword_pos'] = keyword_pos - 1

                execplugins = keyword_tree.get_executable_commands().keys()
                execplugins.sort()

                conflicting_commands = 0
                executable_commands = []

                for plugin in execplugins:
                    if plugin_scope is None or plugin_scope == plugin:
                        executable_commands += [keyword_tree.get_executable_commands()[plugin]]

                        if keyword_tree.get_executable_commands()[plugin].is_conflict_allowed():
                            conflicting_commands += 1

                if (conflicting_commands is 0 and len(executable_commands) >= 1) or \
                    (conflicting_commands is 1 and len(executable_commands) is 1):

                    statusdict['status'] = 'exec_commands'
                    statusdict['commands'] = executable_commands

                elif conflicting_commands > 1:
                    statusdict['status'] = 'command_conflict'
                    statusdict['commands'] = executable_commands

                else:
                    statusdict['status'] = 'no_command_match'
                    statusdict['commands'] = executable_commands

                break

            if len(matching_keywords) is 1:
                # Only one match, dig deeper in the keyword tree
                keyword_tree = keyword_tree.get_sub_keyword(matching_keywords[0])
                statusdict['expanded_label'] = self.merge_keywords([statusdict['expanded_label']] + [matching_keywords[0]])
                keyword_pos += 1

            elif len(matching_keywords) is 0:
                statusdict['status'] = 'no_label_match'
                break

            elif len(matching_keywords) > 1:
                statusdict['status'] = 'label_conflict'
                break

            else:
                statusdict['status'] = ('ERROR: Command analysis failed with user input "%s" in mode %s' % (line, self.mode))
                break

        self.logger.debug('-' * 50)
        self.logger.debug('Line analysis ended for line "%s" in mode %s' % (line, self.mode))
        self.logger.debug('Analysis is: \n' + pp.pformat(statusdict))

        return statusdict

    def print_cli_error(self, pos, errmsg):
        '''
        '''
        if self.is_interactive:
            prefix = ''.ljust(pos) + ' ^---+ '
        else:
            prefix = 'CLI Error: '

        print prefix + errmsg

    def print_conflict_keywords(self, statusdict):
        '''
        '''
        sep = 30
        print
        print '  %s %s' % ('Keyword'.ljust(sep), 'Plugins')
        print '  %s %s' % ('======='.ljust(sep), '=======')
        for matching_keyword in statusdict['matching_keywords']:
            print '  %s %s' % (matching_keyword.ljust(sep), ','.join(statusdict['keyword_tree'].get_plugins()))

        print

    def print_help_message(self, command_list):
        '''
        '''
        for command in command_list:
            print "printing help message for %s" % command

    def preloop(self):
        '''
        '''
        try:
            for plugin in self.plugins:
                plugin.enter_mode(self)
        except Exception as e:
            self.logger.warning('Plugin %s failed initializing mode %s:\n%s') % (plugin.get_name(), self.mode, str(e))

    def postloop(self):
        '''
        '''
        try:
            for plugin in self.plugins:
                plugin.leave_mode(self)
        except Exception as e:
            self.logger.warning('Plugin %s failed leaving mode %s:\n%s') % (plugin.get_name(), self.mode, str(e))

    def emptyline(self):
        """Override the default emptyline and return a blank line."""
        pass

    def parseline(self, line):
        """
        We must override the parseline to preverse leading whitespace for
        proper help.

        Since cmd is an old style class, it must be redefined
        """
        # line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        elif line[0] == '!':
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        i, n = 0, len(line)
        while i < n and line[i] in self.identchars:
            i = i + 1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    def update_window_size(self, width, height):
        '''
        '''
        assert isinstance(width, int)
        assert isinstance(height, int)

        self.width = width
        self.height = height

        self.logger.debug('Updating window size width x height : %s x %s' % (width, height))
