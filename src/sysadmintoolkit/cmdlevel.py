from sysadmintoolkit import exception


class _CmdLevel(object):
    '''
    '''
    def __init__(self, label=None, depth=0):
        '''
        '''
        self.label = label

        self.depth = depth

        # Pluginname to Plugin mapping
        self.plugins = {}

        # Pluginname to Commands mapping
        self.executable_commands = {}

        # Registered help for this CmdLevel
        # Pluginname to str mapping
        self.help = {}

        # Sub CmdLevels
        self.sub_cmd_levels = {}

    def add_cmd_level(self, keyword):
        '''
        '''
        self.sub_cmd_levels[keyword] = _CmdLevel(keyword=keyword, depth=self.get_depth() + 1)

    def add_command(self, label, command):
        '''
        '''
        if command.getPlugin().getPluginName() not in self.executable_commands:
            self.executable_commands[command.getPlugin().getPluginName()] = command
        else:
            raise exception.PluginError('Error registering label "%s" from plugin %s, a label already exists from this module' % (command.getLabel(), command.getPlugin()))

        keyword_list = label.split(' ')

        if len(keyword_list) is 0:
            # No more keywords, command is to be inserted at this level
            self.executable_commands[command.getLabel()] = command
        else:
            if keyword_list[0] in self.get_sub_cmd_levels_keywords():
                # Subcmd for this keyword does not exists
                self.add_cmd_level(keyword_list[0])

            self.sub_cmd_levels[keyword_list[0]].add_command(' '.join(keyword_list[1:]), command)

    def is_executable(self):
        return len(self.executable_commands.keys()) > 0

    def get_depth(self):
        '''
        '''
        return self.depth

    def get_sub_cmd_levels(self):
        '''
        '''
        return self.sub_cmd_levels

    def get_sub_cmd_levels_keywords(self):
        keywords = self.sub_cmd_levels.keys()
        keywords.sort()

        return keywords

    def get_label(self):
        '''
        '''
        return self.label
