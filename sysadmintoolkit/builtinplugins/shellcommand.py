import sysadmintoolkit
import subprocess
import types

global plugin_instance

plugin_instance = None


def get_plugin(config, logger):
    '''
    '''
    global plugin_instance

    if plugin_instance is None:
        plugin_instance = ShellCommand(logger, config)

    return plugin_instance


class ShellCommand(sysadmintoolkit.plugin.Plugin):
    '''
    '''
    def __init__(self, logger, config):
        super(ShellCommand, self).__init__("shellcommand", logger, config)

        default_command_help = 'No help available for this command'
        self.shellcommands = {}

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
            def label_function(self, line, mode):
                self.logger.info('Executing shell command: %s' % self.shellcommands[line]['cmd'])

                return subprocess.call(self.shellcommands[line]['cmd'], shell=True)

            label_function.__doc__ = self.shellcommands[label]['shorthelp']

            label_command = sysadmintoolkit.command.ExecCommand(label, self, types.MethodType(label_function, self))

            self.add_command(label_command)
