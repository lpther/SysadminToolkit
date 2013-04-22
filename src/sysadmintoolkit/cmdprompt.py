from sysadmintoolkit import logger, command, exception, cmdlevel
import cmd
import readline


class CmdPrompt(cmd.Cmd):
    '''
    '''

    def __init__(self, logger_, completekey='tab', stdin=None, stdout=None,
                 mode="generic"):
        '''
        '''
        cmd.Cmd.__init__(self, completekey='tab', stdin=None, stdout=None)

        if isinstance(logger_, logger.NullLogger):
            self.logger = logger_
        else:
            raise exception.CommandPromptError('Could not initialize command prompt: Wrong logger class', errno=101)

        if isinstance(mode, str):
            self.mode = mode
        else:
            raise exception.CommandPromptError('Could not initialize command prompt: Mode should be a string', errno=101)

        self.logger.log_debug('New command prompt in mode %s ' % mode)

        # Switching readline delims for allowed characters
        readline.set_completer_delims('')

        # Print out a few CLI debugging info
        print "  raw readline completer delims='%s'" % readline.get_completer_delims().__repr__()

        # Root of the command tree
        self.command_tree = cmdlevel._CmdLevel()

        # Global help is removed from Cmd class and handled in this subclass
        del cmd.Cmd.do_help
        del cmd.Cmd.complete_help

        self.prompt = 'sysadmin-toolkit# '

    def add_default_modules(self):
        '''
        '''
        pass

    def register_command(self, command_):
        '''
        '''
        if not isinstance(command_, command.Command):
            raise exception.PluginError('Error initializing Command Prompt: register_command requires Command class ', errno=301)

    # Redefining commands from cmd.CMD

    def default(self, line):
        """
        """
        self.logger.log_debug("Command Prompt: default: line='%s'" % (line.__repr__()))

    def complete_default(self, text, line, begidx, endidx):
        """
        """
        self.logger.log_debug("Command Prompt: completedefault: text='%s' line='%s' begidx=%s endidx=%s" % (text, line, begidx, endidx))

        return []

    def complete(self, text, state):
        """
        """
        self.logger.log_debug("\nCommand Prompt: complete: text='%s' state=%s" % (text, state))
        self.logger.log_debug("  completiontype=%s" % (readline.get_completion_type()))

    def update_window_size(self, row, col):
        '''
        '''
        assert isinstance(row, int)
        assert isinstance(col, int)

        self.logger.log_debug('Updating window size row x col : %s x %s' % (row, col))

        self.row = row
        self.col = col

    def get_window_row(self):
        return self.row

    def get_window_col(self):
        return self.col
