from sysadmintoolkit import command, exception, cmdlevel, plugin
import cmd
import readline
import logging


def split_label(label):
    '''Returns a list of keywords from the label
    '''
    if isinstance(label, str):
        return label.split(' ')
    else:
        raise exception.SysadminToolkitError('Label is not string type')


def merge_keywords(keywords):
    '''Returns a label from the list of keywords
    '''
    if isinstance(keywords, list):
        for item in keywords:
            if not isinstance(item, str):
                raise exception.SysadminToolkitError('Keyword is not str type')

        if '' in keywords:
            keywords.remove('')

        return ' '.join(keywords)
    else:
        raise exception.SysadminToolkitError('Keywords is not list type')


class CmdPrompt(cmd.Cmd):
    '''
    '''

    def __init__(self, logger_, completekey='tab', stdin=None, stdout=None,
                 mode="generic"):
        '''
        '''
        cmd.Cmd.__init__(self, completekey='tab', stdin=None, stdout=None)

        if isinstance(logger_, logging.Logger):
            self.logger = logger_
        else:
            raise exception.CommandPromptError('Could not initialize command prompt: Wrong logger class', errno=101)

        if isinstance(mode, str):
            self.mode = mode
        else:
            raise exception.CommandPromptError('Could not initialize command prompt: Mode should be a string', errno=101)

        self.logger.debug('New command prompt in mode %s ' % mode)

        # Switching readline delims for allowed characters
        readline.set_completer_delims(' \n')

        self.logger.debug('  raw readline completer delims="%s"' % readline.get_completer_delims().__repr__())
        self.logger.debug('  identchars="%s"' % self.identchars)

        # Root of the command tree
        self.command_tree = cmdlevel._CmdLevel(logger_)

        # List of registered plugins
        self.plugins = []

        # Global help is removed from Cmd class and handled in this subclass
        # del cmd.Cmd.do_help
        # del cmd.Cmd.complete_help

        self.prompt = 'sysadmin-toolkit# '

    def add_plugin(self, plugin_):
        '''Adds the plugin to cmdprompt, and registers the plugin's label to the cmdprompt
        '''
        if not isinstance(plugin_, plugin.Plugin):
            raise exception.PluginError('Error initializing Command Prompt: add_plugin requires Plugin class ', errno=301)

        self.logger.debug('Adding plugin %s in mode %s' % (plugin_.get_name(), self.mode))

        # Add plugin's commands for current mode
        for command in plugin_.get_commands(self.mode):
            self.register_command(command, split_label(command.get_label()))

        for command in plugin_.get_commands(''):
            self.register_command(command)

    def register_command(self, command_):
        '''
        '''
        if not isinstance(command_, command.Command):
            raise exception.PluginError('Error initializing Command Prompt: register_command requires Command class ', errno=301)

        self.logger.debug('Registering command label "%s" into command tree' % (command_.get_label()))

        self.command_tree.add_command(split_label(command_.get_label()), command_)

    # Redefining commands from cmd.CMD

    def default(self, line):
        """
        """
        self.logger.debug("Command Prompt: default: line='%s'" % (line))
        self.logger.debug("  lastcmd='%s'" % (self.lastcmd))
        self.logger.debug("  readlinebuff='%s'" % (readline.get_line_buffer()))

    def complete_default(self, text, line, begidx, endidx):
        """
        """
        self.logger.debug("Command Prompt: completedefault: text='%s' line='%s' begidx=%s endidx=%s" % (text, line, begidx, endidx))
        self.logger.debug("  lastcmd='%s'" % (self.lastcmd))
        self.logger.debug("  readlinebuff='%s'" % (readline.get_line_buffer()))

        return []

    def complete(self, text, state):
        """
        """
        self.logger.debug("\nCommand Prompt: complete: text='%s' state=%s" % (text, state))
        self.logger.debug("  completiontype=%s" % (readline.get_completion_type()))
        self.logger.debug("  lastcmd='%s'" % (self.lastcmd))
        self.logger.debug("  readlinebuff='%s'" % (readline.get_line_buffer()))

    def update_window_size(self, row, col):
        '''
        '''
        assert isinstance(row, int)
        assert isinstance(col, int)

        self.logger.debug('Updating window size row x col : %s x %s' % (row, col))

        self.row = row
        self.col = col

    def get_window_row(self):
        return self.row

    def get_window_col(self):
        return self.col
