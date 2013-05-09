import sysadmintoolkit
import cmd
import readline
import logging
import pprint
import subprocess
import sys


EXIT_THIS_CMDPROMPT = -12345
EXIT_ALL_CMDPROMPT = -12346


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
                            keywords += [current_keyword + ' ']
                            current_keyword = token

                    return keywords + [current_keyword + ' ']

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
        # readline.set_completion_display_matches_hook(self.readline_display_matches_hook)

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

    def default(self, line, plugin_scope=None):
        """
        Handle command line input and take appropriate action
        """
        self.logger.debug("Command Prompt: default: line='%s'" % (line))
        self.logger.debug("  lastcmd='%s'" % (self.lastcmd))
        self.logger.debug("  readlinebuff='%s'" % (readline.get_line_buffer()))
        self.logger.debug("  plugin_scope='%s'" % (plugin_scope))

        user_input = _UserInput(line, self, plugin_scope)

        if user_input.status.startswith('exec_commands'):
            # The command matches to a label in the keyword tree
            # Action: Execute the command (if allowed by the commands)
            executable_commands = user_input.keyword_list[-1].get_executable_commands()

            # Build up the line to pass to the plugin
            keywords_for_plugin = []
            for index in range(len(user_input.matching_static_keyword_list)):
                if not self.is_dynamic_keyword(user_input.matching_static_keyword_list[index][0]):
                    keywords_for_plugin.append(user_input.matching_static_keyword_list[index][0])
                else:
                    keywords_for_plugin.append(user_input.matching_dyn_keyword_list[index][0])

            keys = executable_commands.keys()
            keys.sort()

            last_return_code = 401

            # Redirect output to a new process
            if user_input.status is 'exec_commands_with_pipe':
                if self.shell_allowed:
                    pipe_command_process = subprocess.Popen(user_input.rest_of_line, shell=True, stdin=subprocess.PIPE)
                    sys.stdout = pipe_command_process.stdin
                else:
                    self.logger.warning('Shell interaction is not allowed, pipe ignored')

            for keycmd in keys:
                try:
                    if len(keys) > 1:
                        print ' ***** Executing command from %s *****' % executable_commands[keycmd].get_plugin().get_name()

                    last_return_code = executable_commands[keycmd].get_function()(self.merge_keywords(keywords_for_plugin), self.mode)

                    if last_return_code is None:
                        last_return_code = 0

                except Exception as e:
                    self.logger.error('Error executing label %s with plugin %s in mode %s:\n%s' % \
                                 (' '.join([user_input.matching_static_keyword_list[i][0] for i in range(len(user_input.matching_static_keyword_list))]), \
                                  executable_commands[keycmd].get_plugin().get_name(), self.mode, str(e)))

                    print '>> Error in command execution (see logs for details) : %s' % str(e).split()[0]

                try:
                    if last_return_code is None:
                        last_return_code = 0
                    else:
                        last_return_code = int(last_return_code)
                except:
                    self.logger.warning('Plugin %s, label "%s" returned an invalid value' % \
                                        (' '.join([user_input.matching_static_keyword_list[i][0] for i in range(len(user_input.matching_static_keyword_list))]), \
                                         executable_commands[keycmd].get_plugin().get_name()))

            if user_input.status is 'exec_commands_with_pipe' and self.shell_allowed:
                sys.stdout.close()
                pipe_command_process.wait()
                sys.stdout = sys.__stdout__

        else:
            last_return_code = self.print_error_on_user_input(user_input)

        # This must be here to prevent a leading whitespace in the prompt
        sys.stdout.write('')

        if not self.is_interactive:
            return last_return_code
        else:
            if last_return_code is EXIT_THIS_CMDPROMPT:
                self.logger.debug('Command Prompt exiting mode %s' % self.mode)
                return EXIT_THIS_CMDPROMPT
            elif last_return_code is EXIT_ALL_CMDPROMPT:
                self.logger.debug('Command Prompt exiting program (mode %s)' % self.mode)
                return EXIT_ALL_CMDPROMPT
            else:
                return

    def complete(self, text, state, plugin_scope=None):
        '''
        '''
        if state is 0:
            original_line = readline.get_line_buffer()

            completion_line = original_line[0:readline.get_endidx()]

            self.logger.debug('Command auto completion, user input: "%s", state is %s, completion_type is %s' \
                              % (original_line, state, readline.get_completion_type()))
            self.logger.debug('  begidx=%s endidx=%s completion_line="%s"' % (readline.get_begidx(), readline.get_endidx(), completion_line))

            self.completion_user_input = _UserInput(completion_line, self, plugin_scope, completion=True)

            self.logger.debug('Completion matches are %s' % self.completion_user_input.completion_matches)

            if len(self.completion_user_input.completion_matches) is 0 or \
            (self.completion_user_input.status is 'label_conflict' and self.completion_user_input.input_keyword_list[-1] is not '' and self.completion_user_input.rest_of_line is not ''):
                self.print_error_on_user_input(self.completion_user_input)
                self.completion_matches = []
            elif len(self.completion_user_input.completion_matches) is 1:
                self.completion_user_input.completion_matches[0] += ' '

        try:
            return self.completion_user_input.completion_matches[state]
        except IndexError:
            return None

    def readline_display_matches_hook(self, substitution, matches, longest_match_length):
        self.logger.debug('Readline display matches hook:\n substitution=%s, matches=%s longtest_match_length=%s' % \
                          (substitution, matches, longest_match_length))

        print

        for match in matches:
                print match

        print "%s%s" % (self.prompt, readline.get_line_buffer()),
        readline.redisplay()

    def print_error_on_user_input(self, user_input):
        ok_keywords = ''.join(self.split_label(user_input.rawcmd, preserve_spaces=True)[:len(user_input.input_keyword_list) - 1])

        leading_whitespaces = len(user_input.rawcmd) - len(user_input.rawcmd.lstrip())

        return_code = 301

        if user_input.completion:
            print

        if user_input.status is 'no_label_match':
            # More than one label matches the keyword
            # Action: Display error message about the conflicting keyword
            self.print_cli_error(len(self.prompt + ok_keywords) + leading_whitespaces, 'No matching command found!')
            return_code = 411

        elif user_input.status is 'label_conflict':
            # More than one label matches the keyword
            # Action: Display error message about the conflicting keyword
            self.print_cli_error(len(self.prompt + ok_keywords) + leading_whitespaces, 'Conflict found! Either type "use <plugin> cmd" or type the complete command')

            # The conflict is not at the end of the command
            # Action: Display conflicting keywords and their related plugins
            self.print_conflict_keywords(user_input)
            return_code = 404

        elif user_input.status is 'command_conflict':
            # One or more commands are executable, but they do not allow conflict
            # Action: Display error message
            self.print_cli_error(len(self.prompt + ok_keywords) + leading_whitespaces, 'Command conflict detected, type "use <plugin> cmd" to specify plugin !')
            return_code = 403

        elif user_input.status is 'no_command_match':
            # There is a matching label but no matching executable command
            # Action: Display error message for the keyword
            if user_input.scope is None:
                self.print_cli_error(len(self.prompt + ok_keywords) + leading_whitespaces, 'No executable command found !')
            else:
                self.print_cli_error(len(self.prompt + ok_keywords) + leading_whitespaces, 'No executable command found for plugin %s !' % user_input.scope)
            return_code = 410

        elif user_input.status is 'dynamic_keyword_conflict':
            # There is more than one match, in more than one dynamic keyword type
            # Action: Display conflicting dynamix keywords and their related plugins
            self.print_conflict_keywords(user_input)

            return_code = 404
        else:
            # We should never get here, warning message and dabug if available
            self.logger.warn('Command prompt was unable to parse line %s' % user_input.rawcmd)
            self.logger.debug('UserInput analysis:\n%s' % str(user_input))

            return_code = 301

        if user_input.completion:
            print "%s%s" % (self.prompt, readline.get_line_buffer()),
            readline.redisplay()

        return return_code

    def print_cli_error(self, pos, errmsg):
        '''
        '''
        if self.is_interactive:
            prefix = ''.ljust(pos) + '^--- '
        else:
            prefix = 'CLI Error: '

        print prefix + errmsg

    def print_conflict_keywords(self, user_input):
        '''
        '''
        sep = 30
        print
        print '  %s %s' % ('Keyword'.ljust(sep), 'Plugins')
        print '  %s %s' % ('======='.ljust(sep), '=======')
        for matching_keyword in user_input.matching_static_keyword_list[-1]:
            print '  %s %s' % (matching_keyword.ljust(sep), ', '.join(user_input.keyword_list[-1].get_sub_keyword(matching_keyword).get_plugins()))

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
            self.logger.warning('Plugin %s failed leaving mode %s:\n%s' % (plugin.get_name(), self.mode, str(e)))

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

    def cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.

        """

        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey + ": complete")
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro) + "\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            # sys.stdout.write('')
                            line = raw_input(self.prompt)
                        except EOFError:
                            line = 'EOF'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = 'EOF'
                        else:
                            line = line.rstrip('\r\n')
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass

    def update_window_size(self, width, height):
        '''
        '''
        self.width = width
        self.height = height

        self.logger.debug('Updating window size width x height : %s x %s' % (width, height))


class _UserInput(object):
    '''
    '''
    def __init__(self, rawcmd, cmdprompt, scope=None, completion=False):
        self.rawcmd = rawcmd
        self.cmdprompt = cmdprompt
        self.scope = scope
        self.status = 'not_analyzed'

        # Rest of rawcmd that was not yet analyzed
        self.rest_of_line = rawcmd

        # Each expanded input keywords as entered
        self.input_keyword_list = []

        # Matching keywords for all levels (with unresolved dynamic keywords)
        self.matching_static_keyword_list = []

        # List of {dyn_keywords:{plugin:shorthelp}}
        self.matching_dyn_keyword_list = []

        # Match type for all keywords
        self.matching_keyword_type_list = []

        # List of _Keyword for all positions
        self.keyword_list = [self.cmdprompt.command_tree]

        # List of {dyn_keywords:{plugin:shorthelp}}
        self.dyn_keywords = []

        # List of commands to execute
        self.executable_commands = []

        # Analyze for completion
        self.completion = completion

        self.completion_last_keyword_empty_str = len(self.rawcmd) is 0 or self.rawcmd[-1] is ' '

        self.completion_matches = []

        self.analyze_cmd()

    def __str__(self):
        pp = pprint.PrettyPrinter(indent=4)

        outstr = []

        outstr.append('rawcmd="%s" scope=%s' % (self.rawcmd, self.scope))
        outstr.append('input_keyword_list=%s' % pp.pformat(self.input_keyword_list))
        outstr.append('matching_static_keyword_list=%s' % pp.pformat(self.matching_static_keyword_list))
        outstr.append('matching_dyn_keyword_list=%s' % pp.pformat(self.matching_dyn_keyword_list))
        outstr.append('dyn_keywords=%s' % pp.pformat(self.dyn_keywords))
        outstr.append('match_types=%s' % pp.pformat(self.matching_keyword_type_list))
        outstr.append('rest_of_line="%s" completion_last_kw_empty_str=%s' % (self.rest_of_line, self.completion_last_keyword_empty_str))
        outstr.append('status=%s' % self.status)

        return '  ' + '\n  '.join(outstr)

    def analyze_cmd(self):
        self.cmdprompt.logger.debug('Line analysis started for line "%s" in mode %s (scope is %s)' % \
                                     (self.rawcmd, self.cmdprompt.mode, self.scope))

        while True:
            [this_keyword, self.rest_of_line] = CmdPrompt.split_label(self.rest_of_line, first_keyword_only=True)

            # Get all possibilities from static and dynamic keywords

            possible_static_keywords = self.keyword_list[-1].get_sub_keywords_keys()

            self.dyn_keywords.append(self.keyword_list[-1].get_sub_keyword_dyn_keyword_possibilities(self.cmdprompt.mode))

            matching_static_keywords = sysadmintoolkit.utils.get_matching_prefix(this_keyword, possible_static_keywords)
            matching_dynamic_keywords = sysadmintoolkit.utils.get_matching_prefix(this_keyword, self.dyn_keywords[-1].keys())

            # Prioritize matchign of static keywords over dynamic
            match_type = 'no_match'

            if len(matching_static_keywords) > 0:
                self.matching_static_keyword_list.append(matching_static_keywords)
                match_type = 'static'
            else:
                matching_dyn_keyword_labels = []

                for dyn_keyword in matching_dynamic_keywords:
                    # Iterate over plugins!!!
                    for plugin in self.dyn_keywords[-1][dyn_keyword]:
                        if self.dyn_keywords[-1][dyn_keyword][plugin]['dyn_keyword_label'] not in matching_dyn_keyword_labels:
                            matching_dyn_keyword_labels.append(self.dyn_keywords[-1][dyn_keyword][plugin]['dyn_keyword_label'])
                        match_type = 'dynamic'

                self.matching_static_keyword_list.append(matching_dyn_keyword_labels)

            self.matching_keyword_type_list.append(match_type)
            self.matching_dyn_keyword_list.append(matching_dynamic_keywords)

            self.cmdprompt.logger.debug('-' * 50)
            self.cmdprompt.logger.debug('this_keyword="%s" rest_of_line="%s"' % (this_keyword, self.rest_of_line))
            self.cmdprompt.logger.debug('possible_keywords=%s' % possible_static_keywords)
            self.cmdprompt.logger.debug('matching_keywords="%s"' % self.matching_static_keyword_list[-1])
            self.cmdprompt.logger.debug('matching_static=%s' % matching_static_keywords)
            self.cmdprompt.logger.debug('matching_dynamic=%s' % matching_dynamic_keywords)

            self.input_keyword_list.append(this_keyword)

            if (this_keyword is '' or this_keyword.startswith('|')) and \
            (not self.completion or \
            (self.completion and not self.completion_last_keyword_empty_str)):
                # End of user input for this label
                if not self.completion or (self.completion and not self.completion_last_keyword_empty_str):
                    self.input_keyword_list.pop()
                    self.matching_static_keyword_list.pop()
                    self.matching_keyword_type_list.pop()
                    self.dyn_keywords.pop()
                    self.matching_dyn_keyword_list.pop()

                execplugins = self.keyword_list[-1].get_executable_commands().keys()
                execplugins.sort()

                conflicting_commands = 0
                executable_commands = []

                for plugin in execplugins:
                    if self.scope is None or self.scope == plugin:
                        executable_commands += [self.keyword_list[-1].get_executable_commands()[plugin]]

                        if not executable_commands[-1].is_conflict_allowed():
                            conflicting_commands += 1

                if (conflicting_commands is 0 and len(executable_commands) >= 1) or \
                    (conflicting_commands is 1 and len(executable_commands) is 1):

                    if this_keyword is '':
                        self.status = 'exec_commands'
                    elif this_keyword.startswith('|'):
                        self.status = 'exec_commands_with_pipe'
                        self.rest_of_line = '%s %s' % (this_keyword[1:], self.rest_of_line)

                elif conflicting_commands > 1:
                    self.status = 'command_conflict'

                else:
                    self.status = 'no_command_match'

                self.executable_commands = executable_commands

                break

            elif len(self.matching_static_keyword_list[-1]) is 1 or \
            (len(self.matching_static_keyword_list[-1]) is 1 and self.completion and self.completion_last_keyword_empty_str):
                # Only one match, dig deeper in the keyword tree
                if this_keyword is '' and self.completion:
                    self.completion_last_keyword_empty_str = False

                self.keyword_list.append(self.keyword_list[-1].get_sub_keyword(self.matching_static_keyword_list[-1][0]))

            elif len(self.matching_static_keyword_list[-1]) is 0:
                self.status = 'no_label_match'
                break

            elif len(self.matching_static_keyword_list[-1]) > 1:
                if self.matching_keyword_type_list[-1] is 'static':
                    self.status = 'label_conflict'
                else:
                    self.status = 'dynamic_keyword_conflict'

                break

            else:
                self.status = 'ERROR: Command analysis failed with user input "%s" in mode %s' % (self.rawcmd, self.mode)
                break

        for k in self.matching_static_keyword_list[-1] + self.matching_dyn_keyword_list[-1]:
            if not CmdPrompt.is_dynamic_keyword(k):
                self.completion_matches.append(k)

        self.completion_matches.sort()

        self.cmdprompt.logger.debug('-' * 50)
        self.cmdprompt.logger.debug('Line analysis ended for line "%s" in mode %s' % (self.rawcmd, self.cmdprompt.mode))
        self.cmdprompt.logger.debug('Analysis is: \n%s' % self)
