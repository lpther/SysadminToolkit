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
                                        (for help printing)
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

        if statusdict['status'] is 'match':
            # The command matches to a label in the keyword tree
            # Action: Execute the command (if allowed by the commands)
            print "we have a match with %s" % line
            executable_commands = statusdict['keyword_tree'].get_executable_commands()

            keys = executable_commands.keys()
            keys.sort()

            for keycmd in keys:
                executable_commands[keycmd].get_function()(line, self.mode)
            # return execute_command(self, statusdict, line)

        elif statusdict['status'] is 'no_match':
            # There is no matching label in the keyword tree,
            # Action: Display error message for the bad keyword
            ok_keywords = ''.join(self.split_label(line, preserve_spaces=True)[:statusdict['keyword_pos'] - 1])

            self.print_cli_error(len(self.prompt + ok_keywords), 'No matching command found !')

            if not self.is_interactive:
                return 1
            else:
                return

        elif statusdict['status'] is 'conflict':
            # More than one label matches the keyword
            # Action: Display error message about the conflicting keyword
            ok_keywords = ''.join(self.split_label(line, preserve_spaces=True)[:statusdict['keyword_pos'] - 1])

            self.print_cli_error(len(self.prompt + ok_keywords), 'Conflict found! Either type "use <plugin> cmd" or type the complete command')

            # The conflict is not at the end of the command
            # Action: Display conflicting keywords and their related plugins
            self.print_conflict_keywords(statusdict)

            if not self.is_interactive:
                return 1
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

            if this_keyword is '':
                # End of user input for this label
                statusdict['status'] = 'match'
                statusdict['keyword_pos'] = keyword_pos - 1
                break

            if len(matching_keywords) is 1:
                # Only one match, dig deeper in the keyword tree
                keyword_tree = keyword_tree.get_sub_keyword(matching_keywords[0])
                statusdict['expanded_label'] = self.merge_keywords([statusdict['expanded_label']] + [matching_keywords[0]])
                keyword_pos += 1

            elif len(matching_keywords) is 0:
                statusdict['status'] = 'no_match'
                break

            elif len(matching_keywords) > 1:
                statusdict['status'] = 'conflict'
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
        print ''.ljust(pos) + ' ^---+ %s' % errmsg

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

    def update_window_size(self, width, height):
        '''
        '''
        assert isinstance(width, int)
        assert isinstance(height, int)

        self.width = width
        self.height = height

        self.logger.debug('Updating window size width x height : %s x %s' % (width, height))
