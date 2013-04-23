from sysadmintoolkit import exception
import logging


class Plugin(object):
    '''
    '''

    def __init__(self, name, logger_):
        '''
        '''
        if isinstance(name, str):
            self.name = name
        else:
            raise exception.CommandPromptError('Error initializing plugin : Plugin name requires a string (1st arg)', errno=302)

        if isinstance(logger_, logging.Logger):
            self.logger = logger_
        else:
            raise exception.CommandPromptError('Error initializing plugin : logger requires a Logger instance (2nd arg)', errno=302)

        # Plugin's current mode
        self.currentmode = None

        # Plugin's function to label and mode mapping
        # labelmap[mode] = {}
        # labelmap[mode][label] = function
        self.labelmap = { '' : {} }

    def add_command(self, command_, modes=[]):
        '''
        mode    [str]    list of allowed modes for this label.
                         Empty list all modes allowed.
        '''
        from sysadmintoolkit import command

        if not isinstance(command_, command.Command):
                raise exception.PluginError('Error adding label : Wrong command type', errno=401)

        if isinstance(modes, list):
            # Default mode is expected
            if len(modes) is 0:
                modes = ['']

            for mode in modes:
                if isinstance(mode, str):
                    self.labelmap[mode][command_.get_label()] = command_
                else:
                    raise exception.PluginError('Error adding label : Wrong mode type', errno=401)

        else:
            raise exception.PluginError('Error adding label : Label allowed mode requires a list of string', errno=401)

        self.logger.debug('Plugin %s added command "%s" to modes %s' % (command_.get_plugin().get_name(), command_.get_label(), modes))

    # Undefined stuff

    def get_commands(self, mode):
        '''Returns the list of commands for the requested mode
        '''
        if mode not in self.labelmap:
            return []
        else:
            labels = self.labelmap[mode].keys()

            command_list = []

            for label in labels:
                command_list += [self.labelmap[mode][label]]

        return command_list

    def enter_mode(self, mode):
        '''
        '''
        self.register_labels(mode)

    def leave_mode(self, mode):
        '''
        '''
        pass

    def get_name(self):
        '''
        '''
        return self.name

    def get_current_mode(self):
        '''
        '''
        return self.currentmode

    def get_dynamic_keyword_list(self, keyword):
        '''
        '''
        return []
