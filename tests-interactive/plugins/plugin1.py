from sysadmintoolkit import plugin, command
import logging


global plugin_instance

plugin_instance = None


def get_plugin(config, logger):
    '''
    '''
    global plugin_instance

    if plugin_instance is None:
        plugin_instance = BehavedDynamicPlugin('plugin1')

    return plugin_instance


class DummyPlugin(plugin.Plugin):
    def __init__(self, name):
        logger = logging.getLogger('DummyPlugin')
        logger.addHandler(logging.NullHandler)

        config = {}

        super(DummyPlugin, self).__init__(name, logger, config)

        self.add_command(command.LabelHelp('dummyplugin is ready', self, 'shorthelp for dummyplugin is ready'))

        self.last_state = 'init'


class BehavedDynamicPlugin(DummyPlugin):
    def __init__(self, name):
        super(BehavedDynamicPlugin, self).__init__(name)

        self.add_command(command.ExecCommand('unique %s <fruit> command' % self.name, self, self.behaved_function_1))
        self.add_command(command.ExecCommand('unique %s <fruit> command <fruit>' % self.name, self, self.behaved_function_1))
        self.add_command(command.ExecCommand('universal %s command' % self.name, self, self.behaved_function_1))
        self.add_command(command.ExecCommand('conflicting <fruit> command', self, self.behaved_function_1))
        self.add_command(command.ExecCommand('conflicting <fruit> command <fruit>', self, self.behaved_function_1))
        self.add_command(command.ExecCommand('non conflicting <fruit> command', self, self.behaved_function_1, allow_conflict=True))
        self.add_command(command.ExecCommand('non conflicting <fruit> command <fruit>', self, self.behaved_function_1, allow_conflict=True))
        self.add_command(command.ExecCommand('reset', self, self.reset_state, allow_conflict=True))

        self.add_dynamic_keyword_fn('<fruit>', self.resolve_dynamic_keyword)

        self.dyn_command_line = ''

    def behaved_function_1(self, line, mode):
        self.last_state = 'plugin %s behaved function 1' % self.name
        self.dyn_command_line = line
        print 'plugin=%s line="%s"' % (self.name, line)
        return 12345

    def resolve_dynamic_keyword(self, dyn_keyword):
        return {'apple': 'This is a green or red fruit', \
                'banana': 'This is a yellow fruit', \
                'apricot': 'This is an orange fruit', \
                'pineapple': 'This is an orange and yellow fruit', \
                }

    def reset_state(self, line, mode):
        self.last_state = 'init'
