import sysadmintoolkit
import cmd
import readline
import logging


class CmdPrompt(cmd.Cmd):
    '''
    '''
    @classmethod
    def split_label(cls, label):
        '''Returns a list of keywords from the label
        '''
        if isinstance(label, str):
            return label.split()
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

    def __init__(self, logger, completekey='tab', stdin=None, stdout=None,
                 mode="generic", shell_allowed=False, prompt='sysadmin-toolkit# '):
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
        readline.set_completer_delims(' \n')

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

        self.prompt = prompt

        self.shell_allowed = shell_allowed

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

    def default(self, line):
        """
        Handle command line input and take appropriate action
        """
        self.logger.debug("Command Prompt: default: line='%s'" % (line))
        self.logger.debug("  lastcmd='%s'" % (self.lastcmd))
        self.logger.debug("  readlinebuff='%s'" % (readline.get_line_buffer()))

        if line in self.command_tree.get_sub_keywords_labels():
            # Line is found as is in the command tree
            label_parameters = self.command_tree.get_sub_keywords_labels()[line]

            if len(label_parameters['executable_commands']) is not 0:
                # At least one command found, label can be executed
                plugin_names = label_parameters['executable_commands'].keys()
                plugin_names.sort()

                for plugin_name in plugin_names:
                    exec_command = label_parameters['executable_commands'][plugin_name]

                    exec_command.get_function()(line, self.mode)

            else:
                # This is not an executable label
                print
                print '>> %s ^ missing input' % (' ' * (len(self.prompt) + len(line) - 2))
        else:
            pass

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

    def update_window_size(self, width, height):
        '''
        '''
        assert isinstance(width, int)
        assert isinstance(height, int)

        self.width = width
        self.height = height

        self.logger.debug('Updating window size width x height : %s x %s' % (width, height))
