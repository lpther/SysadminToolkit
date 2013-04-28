import sysadmintoolkit


class _Keyword(object):
    '''
    '''
    def __init__(self, logger, keyword=None, depth=0):
        '''
        '''
        self.keyword = keyword

        self.depth = depth

        # Pluginname to Plugin mapping
        # All plugins that registered commands that traversed
        # this keyword are added here.
        self.plugins = {}

        # Pluginname to Commands mapping
        self.executable_commands = {}

        # Registered help for this CmdLevel
        # Pluginname to str mapping
        self.help = {}

        self.logger = logger

        # Sub CmdLevels
        self.sub_keywords = {}

        self.reserved_only = False

    def add_keyword_level(self, keyword, command):
        '''
        '''
        if keyword is '*':
            if len(self.get_sub_keywords_keys()) is not 0 and keyword not in self.get_sub_keywords_keys():
                # A * keyword cannot coexist with other subkeywords
                raise sysadmintoolkit.exception.PluginError('Error registering keyword "%s" from plugin %s, other subkeywords already registered '\
                                                             % (command.getkeyword(), command.getPlugin()))

        if '*' in self.get_sub_keywords_keys() and keyword != '*':
            # A * keyword cannot coexist with other subkeywords
            raise sysadmintoolkit.exception.PluginError('Error registering keyword "%s" from plugin %s, other subkeywords already registered '\
                                                         % (command.getkeyword(), command.getPlugin()))

        self.sub_keywords[keyword] = _Keyword(self.logger, keyword=keyword, depth=self.get_depth() + 1)

    def add_command(self, keywords, command):
        '''
        Adds the command to the command tree rooted at this level

        keywords    list    list of keywords relative to the position in the tree
        '''
        # Add the plugin no matter what command type
        if command.get_plugin().get_name() not in self.plugins:
            self.plugins[command.get_plugin().get_name()] = command.get_plugin()

        if len(keywords) is 0:
            # Add the command at the current level depending on type
            if self.reserved_only:
                if not command.is_reserved():
                    raise sysadmintoolkit.exception.PluginError('Error registering keyword "%s" from plugin %s, insertion of a non-reserved ',
                                                                'command in a reserved keyword is not allowed' % (command.getkeyword(), command.getPlugin()))
            if command.is_reserved():
                self.reserved_only = True

            if isinstance(command, sysadmintoolkit.command.ExecCommand):
                if command.get_plugin().get_name() not in self.executable_commands:
                    self.executable_commands[command.get_plugin().get_name()] = command
                else:
                    raise sysadmintoolkit.exception.PluginError('Error registering keyword "%s" from plugin %s, a keyword already exists from this module' % (command.getkeyword(), command.getPlugin()))
            elif isinstance(command, sysadmintoolkit.command.LabelHelp):
                if command.get_plugin().get_name() not in self.help:
                    self.help[command.get_plugin().get_name()] = command
                else:
                    raise sysadmintoolkit.exception.PluginError('Error registering keyword "%s" from plugin %s, a keyword already exists from this module' % (command.getkeyword(), command.getPlugin()))
        else:
            if keywords[0] not in self.sub_keywords:
                self.add_keyword_level(keywords[0], command)

            self.sub_keywords[keywords[0]].add_command(keywords[1:], command)

    def get_sub_keywords_labels(self):
        '''Returns a dict of all sub_keywords labels mapped to a list of properties
        '''
        if self.keyword is None:
            keywords_dict = { }
            localkeyword = ''
        else:
            keywords_dict = { self.keyword: { 'executable_commands': self.executable_commands, \
                                            'help': self.help } }
            localkeyword = self.keyword

        for keyword in self.get_sub_keywords_keys():
            subkeywordsdict = self.sub_keywords[keyword].get_sub_keywords_labels()

            for subkeyword in subkeywordsdict.keys():
                # For each subkeyword, merge with current keyword
                keywords_dict[sysadmintoolkit.cmdprompt.CmdPrompt.merge_keywords([localkeyword] + \
                              sysadmintoolkit.cmdprompt.CmdPrompt.split_label(subkeyword))] = subkeywordsdict[subkeyword]

        return keywords_dict

    def get_sub_keywords_dyn_keywords(self, mode):
        '''
        Returns a map of all sub_keywords that are dynamic, mapped to a list
        of plugins registered to this sub_keyword

        {'<dyn_keyword>':[plugins], etc...}
        '''
        sub_keywords_keys = self.get_sub_keywords_keys()

        sub_dyn_keywords = {}

        for keyword in sub_keywords_keys:
            if sysadmintoolkit.cmdprompt.CmdPrompt.is_dynamic_keyword(keyword):
                sub_dyn_keywords[keyword] = self.get_sub_keyword[keyword].get_plugins()

        return sub_dyn_keywords

    def get_depth(self):
        '''
        '''
        return self.depth

    def get_sub_keywords_keys(self, plugin_scope=None):
        if plugin_scope is None:
            keywords = self.sub_keywords.keys()
            keywords.sort()
        else:
            keywords = []

            for sub_keyword_key in self.sub_keywords.keys():
                if plugin_scope in self.get_sub_keyword(sub_keyword_key).get_plugins():
                    keywords += [sub_keyword_key]

        keywords.sort()
        return keywords

    def get_sub_keyword(self, strkeyword):
        return self.sub_keywords[strkeyword]

    def get_executable_commands(self):
        return self.executable_commands

    def get_plugins(self):
        return self.plugins.keys()
