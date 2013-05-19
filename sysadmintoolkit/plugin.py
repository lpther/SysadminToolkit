import sysadmintoolkit
import collections
import logging


class Plugin(object):
    '''
    '''
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

        self.plugin_set = {}

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
        fn             method     plugin.fn("<mykeyword>") must return a map of 'a_keyword':'shorthelp'
                                  for possible keywords for <mykeyword>
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
        '''
        Returns the list of commands for the requested mode.

        This is called by a newly created command prompt to populate it's available
        labels.

        '''
        if mode not in self.label_map:
            return []
        else:
            labels = self.label_map[mode].keys()

            command_list = []

            for label in labels:
                command_list += [self.label_map[mode][label]]

        return command_list

    def get_dyn_keyword_map(self, dyn_keyword, user_input_obj):
        '''
        Returns map of dyn_keyword possibilities/shorthelp by querying
        registered dyn_keyword functions, for the provided mode.

        Returns:
        {} if no matching registered keywords
        {'possibility1': 'shorthelp for possibility1',
         'possibility2': 'shorthelp for possibility2',
         }

        This is called by a newly created command prompt to populate it's available
        labels.

        '''
        mode = user_input_obj.get_mode()

        self.logger.debug('Dynamic keyword map request for %s in mode %s' % (dyn_keyword, mode))

        if user_input_obj.get_mode() not in self.dyn_keyword_map:
            mode = ''

        if dyn_keyword in self.dyn_keyword_map[mode]:
            return self.dyn_keyword_map[mode][dyn_keyword](user_input_obj)
        else:
            return {}

    def enter_mode(self, cmdprompt):
        '''
        '''
        self.cmdstack += [cmdprompt]

        self.logger.debug('Plugin %s is entering mode %s' % (self.name, cmdprompt.mode))

    def leave_mode(self, cmdprompt):
        '''
        '''
        lastknowncmdprompt = self.cmdstack.pop()

        self.logger.debug('Leaving mode %s (last known mode is %s)' % (cmdprompt.mode, lastknowncmdprompt.mode))

    def get_name(self):
        '''
        '''
        return self.name

    def clear_cache(self):
        '''
        '''
        return

    def update_plugin_set(self, plugin_set):
        self.plugin_set = plugin_set


class PluginSet(object):
    def __init__(self):
        self.plugins = collections.OrderedDict()

    def __str__(self):
        return '[%s]' % ', '.join(self.plugins.keys())

    def add_plugin(self, plugin):
        '''
        Adds a new plugin to the set.

        Note: Will not add or update a plugin that has already been added.
        '''
        if plugin.get_name() not in self.plugins:
            self.plugins[plugin.get_name()] = plugin

    def get_plugins(self):
        return self.plugins

    def clear_cache(self):
        for plugin in self.plugins:
            self.plugins[plugin].clear_cache()
