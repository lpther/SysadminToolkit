import sysadmintoolkit
import logging


class Plugin(object):
    '''
    '''
    plugin = None

    @classmethod
    def get_plugin(cls, config, logger):
        '''
        '''
        if Plugin.plugin is None:
            plugin = Plugin('genericplugin', logger, config)

        return plugin

    def __init__(self, name, logger, config):
        '''
        '''
        if isinstance(name, str):
            self.name = name
        else:
            raise sysadmintoolkit.exception.CommandPromptError('Error initializing plugin : Plugin name requires a string (1st arg)', errno=302)

        if isinstance(logger, logging.Logger):
            self.logger = logger
        else:
            raise sysadmintoolkit.exception.CommandPromptError('Error initializing plugin : logger requires a Logger instance (2nd arg)', errno=302)

        # Command prompts that added this module
        self.cmdstack = []

        # Plugin's function to label and mode mapping
        # labelmap[mode] = {}
        # labelmap[mode][label] = function
        self.label_map = { '' : {} }
        self.dyn_keyword_map = { '': {} }

        self.config = config

    def add_command(self, command, modes=[]):
        '''
        mode    [str]    list of allowed modes for this label.
                         Empty list all modes allowed.
        '''
        if not isinstance(command, sysadmintoolkit.command.Label):
                raise sysadmintoolkit.exception.PluginError('Error adding label : Wrong command type', errno=401)

        if isinstance(modes, list):
            # Default mode is expected
            if len(modes) is 0:
                modes = ['']

            for mode in modes:
                if isinstance(mode, str):
                    self.label_map[mode][command.get_label()] = command
                else:
                    raise sysadmintoolkit.exception.PluginError('Error adding label : Wrong mode type', errno=401)

        else:
            raise sysadmintoolkit.exception.PluginError('Error adding label : Label allowed mode requires a list of string', errno=401)

        self.logger.debug('Plugin %s added command "%s" to modes %s' % (self.get_name(), command.get_label(), modes))

    def add_dynamic_keyword_fn(self, dyn_keyword, fn, modes=[]):
        '''
        dyn_keyword    str        Format: "<mykeyword>"
        fn             method     plugin.fn() must return a list of string
                                  for possible keywords
        '''
        if not isinstance(dyn_keyword, str):
                raise sysadmintoolkit.exception.PluginError('Error adding dynamic keyword in plugin %s : Keyword must be a string' \
                                                            % self.get_name(), errno=402)

        if not isinstance(fn, type(self.add_dynamic_keyword_fn)):
                raise sysadmintoolkit.exception.PluginError('Error adding dynamic keyword in plugin %s : The function type os not correct' \
                                                            % self.get_name(), errno=402)

        if isinstance(modes, list):
            # Default mode is expected
            if len(modes) is 0:
                modes = ['']

            for mode in modes:
                if isinstance(mode, str):
                    self.dyn_keyword_map[mode][dyn_keyword] = fn
                else:
                    raise sysadmintoolkit.exception.PluginError('Error adding dynamic keyword in plugin %s : Wrong mode type' \
                                                                % self.get_name(), errno=402)

        else:
            raise sysadmintoolkit.exception.PluginError('Error adding dynamic keyword in plugin %s : Label allowed mode requires a list of string' \
                                                        % self.get_name(), errno=402)

        self.logger.debug('Plugin %s added dynamic keyword "%s" to modes %s' % (self.get_name(), dyn_keyword, modes))

    def get_commands(self, mode):
        '''Returns the list of commands for the requested mode
        '''
        if mode not in self.label_map:
            return []
        else:
            labels = self.label_map[mode].keys()

            command_list = []

            for label in labels:
                command_list += [self.label_map[mode][label]]

        return command_list

    def get_dyn_keyword_list(self, dyn_keyword, mode):
        if mode not in self.dyn_keyword_map:
            mode = ''

        if dyn_keyword in self.dyn_keyword_map[mode]:
            return self.dyn_keyword_map[mode][dyn_keyword]()
        else:
            return []

    def enter_mode(self, cmdprompt):
        '''
        '''
        self.cmdstack += [cmdprompt]

        self.logger.debug('Entering mode %s' % (cmdprompt.mode))

    def leave_mode(self, cmdprompt):
        '''
        '''
        lastknowncmdprompt = self.cmdstack.pop()

        self.logger.debug('Leaving mode %s (last known mode is %s)' % (cmdprompt.mode, lastknowncmdprompt.mode))

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
