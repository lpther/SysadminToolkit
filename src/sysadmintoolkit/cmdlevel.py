from sysadmintoolkit import exception


class _CmdLevel(object):
    '''
    '''
    def __init__(self, logger, keyword=None, depth=0):
        '''
        '''
        self.keyword = keyword

        self.depth = depth

        # Pluginname to Plugin mapping
        self.plugins = {}

        # Pluginname to Commands mapping
        self.executable_commands = {}

        # Registered help for this CmdLevel
        # Pluginname to str mapping
        self.help = {}

        self.logger = logger

        # Sub CmdLevels
        self.sub_cmd_levels = {}

    def add_cmd_level(self, keyword):
        '''
        '''
        self.sub_cmd_levels[keyword] = _CmdLevel(self.logger, keyword=keyword, depth=self.get_depth() + 1)

    def add_command(self, keywords, command):
        '''
        Adds the command to the command tree rooted at this level

        keywords    list    list of keywords relative to the position in the tree
        '''
        if len(keywords) is 0:
            # Add the command at the current level
            if command.get_plugin().get_name() not in self.executable_commands:
                self.executable_commands[command.get_plugin().get_name()] = command

            else:
                raise exception.PluginError('Error registering keyword "%s" from plugin %s, a keyword already exists from this module' % (command.getkeyword(), command.getPlugin()))

        else:
            if keywords[0] not in self.sub_cmd_levels:
                self.add_cmd_level(keywords[0])

            self.sub_cmd_levels[keywords[0]].add_command(keywords[1:], command)

    def get_subcmd_labels(self):
        '''Returns a dict of all subcmd labels mapped to a list of plugins
        '''
        from sysadmintoolkit import cmdprompt

        if self.keyword is None:
            cmdleveldict = { }
            localkeyword = ''
        else:
            cmdleveldict = {  self.keyword: self.executable_commands }
            localkeyword = self.keyword

        for keyword in self.get_sub_cmd_levels_keywords():
            subcmdleveldict = self.sub_cmd_levels[keyword].get_subcmd_labels()

            print "  ---------------------"
            print "  cmdevelcmddict  %s " % cmdleveldict
            print "  subcmdlevelcmddict  %s " % subcmdleveldict
            print "  ---------------------"
            print

            for subkeyword in subcmdleveldict.keys():
                # For each subkeyword, merge with current keyword
                cmdleveldict[cmdprompt.merge_keywords([localkeyword] + cmdprompt.split_label(subkeyword))] = subcmdleveldict[subkeyword]

        return cmdleveldict

    def is_executable(self):
        return len(self.executable_commands.keys()) > 0

    def get_depth(self):
        '''
        '''
        return self.depth

    def get_sub_cmd_levels_keywords(self):
        keywords = self.sub_cmd_levels.keys()
        keywords.sort()

        return keywords

    def get_keyword(self):
        '''
        '''
        return self.keyword
