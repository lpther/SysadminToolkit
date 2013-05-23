__version__ = "0.1.0a"

import sysadmintoolkit
import subprocess
import types
import collections

global plugin_instance

plugin_instance = None


def get_plugin(logger, config):
    '''
    '''
    global plugin_instance

    if plugin_instance is None:
        plugin_instance = ShellCommand(logger, config)

    return plugin_instance


class ShellCommand(sysadmintoolkit.plugin.Plugin):
    '''
    Description
    -----------

    Adds shell calls to the CLI

    Configuration
    -------------

    *cmd-some_cli_command*
      Define custom commands, the label appearing after the cmd- prefix
      will be available and mapped to the value and executed in a shell.

      Note : escape ";" as they are interpreted as comments

      ex: cmd-my_custom_command = uptime \; ps -ef

    *help-some_cli_command*
      Define a short help definition for you custom command

      ex: help-my_custom_command = Shows the current number of users and load

    Commands listing
    ----------------

    Run *debug shellcommand* to list all registered user commands

    '''
    def __init__(self, logger, config):
        super(ShellCommand, self).__init__("shellcommand", logger, config, version=__version__)

        default_command_help = 'No help available for this command'
        self.shellcommands = collections.OrderedDict()

        command_prefix = 'cmd-'
        command_help_prefix = 'help-'

        for attr, value in self.config.items():
            if attr.startswith(command_prefix):
                try:
                    label = ' '.join(attr[len(command_prefix):].split('_'))
                    label = sysadmintoolkit.cmdprompt.CmdPrompt.merge_keywords(sysadmintoolkit.cmdprompt.CmdPrompt.split_label(label))

                    if label not in self.shellcommands:
                        self.shellcommands[label] = {'cmd': value.replace('\;', ';').replace('\#', '#'), 'shorthelp': default_command_help}
                    else:
                        logger.warning('A command with this label has already been registered: %s' % label)
                except Exception as e:
                    self.logger.error('Invalid label for shellcommand %s: %s' % (attr, e))

        for attr, value in self.config.items():
            if attr.startswith(command_help_prefix):
                try:
                    label = ' '.join(attr[len(command_help_prefix):].split('_'))
                    label = sysadmintoolkit.cmdprompt.CmdPrompt.merge_keywords(sysadmintoolkit.cmdprompt.CmdPrompt.split_label(label))

                    if label in self.shellcommands:
                        self.shellcommands[label]['shorthelp'] = str(value)
                    else:
                        logger.warning('No command defined for this help message: %s' % label)
                except Exception as e:
                    self.logger.error('Invalid label for shellcommand %s: %s' % (attr, e))

        for label in self.shellcommands:
            def label_function(self, user_input_obj):
                self.logger.info('Executing shell command: %s' % self.shellcommands[user_input_obj.get_entered_command()]['cmd'])

                return subprocess.call(self.shellcommands[user_input_obj.get_entered_command()]['cmd'], shell=True)

            label_function.__doc__ = '\n%s\n\nShell command: "%s"' % (self.shellcommands[label]['shorthelp'], self.shellcommands[label]['cmd'])

            shorthelp = self.shellcommands[label]['shorthelp']

            longhelp = '%s\n\nShell command: "%s"' % (shorthelp, self.shellcommands[label]['cmd'])

            label_command = sysadmintoolkit.command.ExecCommand(label, self, types.MethodType(label_function, self), \
                                                                shorthelp=shorthelp, \
                                                                longhelp=longhelp)

            self.add_command(label_command)

        self.add_command(sysadmintoolkit.command.ExecCommand('debug shellcommand', self, self.debug))

        self.logger.info('Plugin shellcommand finished initialization')

    def debug(self, user_input_obj):
        '''
        Display user registered commands
        '''
        lsep = 60

        print 'ShellCommand plugin configuration and state:'
        print
        print '  shellcommand plugin version: %s' % __version__
        print

        if len(self.shellcommands):
            print '  %s %s' % ('Label'.ljust(lsep), 'Shell Command (Help)')
            print

            for label in self.shellcommands:
                print '  %s' % label.ljust(lsep),

                print sysadmintoolkit.utils.indent_text('%s (%s)' % (self.shellcommands[label]['cmd'], self.shellcommands[label]['shorthelp']), len('  %s' % label.ljust(lsep)) + 1, 120).lstrip()
