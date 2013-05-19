import sysadmintoolkit
import pprint


class UserInput(object):
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

        self._analyze_cmd()

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

    def get_mode(self):
        '''
        Returns the command prompt's mode where this command is entered

        '''
        return self.cmdprompt.mode

    def get_entered_command(self):
        '''
        Returns the command as entered by the user (expanded)

        '''
        keywords_for_plugin = []
        for index in range(len(self.matching_static_keyword_list)):
            if not self.cmdprompt.is_dynamic_keyword(self.matching_static_keyword_list[index][0]):
                keywords_for_plugin.append(self.matching_static_keyword_list[index][0])
            else:
                keywords_for_plugin.append(self.matching_dyn_keyword_list[index][0])

        return self.cmdprompt.merge_keywords(keywords_for_plugin)

    def get_static_keyword_list(self):
        return self.matching_static_keyword_list

    def _analyze_cmd(self):
        self.cmdprompt.logger.debug('Line analysis started for line "%s" in mode %s (scope is %s)' % \
                                     (self.rawcmd, self.cmdprompt.mode, self.scope))

        while True:
            [this_keyword, self.rest_of_line] = sysadmintoolkit.cmdprompt.CmdPrompt.split_label(self.rest_of_line, first_keyword_only=True)

            # Get all possibilities from static and dynamic keywords

            possible_static_keywords = self.keyword_list[-1].get_sub_keywords_keys()

            self.dyn_keywords.append(self.keyword_list[-1].get_sub_keyword_dyn_keyword_possibilities(self))

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

                        # If the latest keyword entered matches exactly the possibilities, execute only this one
                        if self.input_keyword_list[-1] in self.matching_dyn_keyword_list[-1]:
                            self.matching_dyn_keyword_list[-1] = [self.input_keyword_list[-1]]

                        if len(self.matching_dyn_keyword_list[-1]) > 1:
                            self.status = 'dynamic_keyword_multiple_prefix'

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
            if not sysadmintoolkit.cmdprompt.CmdPrompt.is_dynamic_keyword(k):
                self.completion_matches.append(k)

        self.completion_matches.sort()

        self.cmdprompt.logger.debug('-' * 50)
        self.cmdprompt.logger.debug('Line analysis ended for line "%s" in mode %s' % (self.rawcmd, self.cmdprompt.mode))
        self.cmdprompt.logger.debug('Analysis is: \n%s' % self)
