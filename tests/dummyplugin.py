from sysadmintoolkit import plugin, command
import logging


class DummyPlugin(plugin.Plugin):
    def __init__(self, name):
        logger = logging.getLogger('DummyPlugin')
        logger.addHandler(logging.NullHandler)

        config = {}

        super(DummyPlugin, self).__init__(name, logger, config)

        self.add_command(command.LabelHelp('dummyplugin is ready', self, 'shorthelp for dummyplugin is ready'))

        self.last_state = 'init'


class BadPlugin(DummyPlugin):
    def __init__(self, name):
        super(BadPlugin, self).__init__(name)

        self.add_command(command.ExecCommand('execute bad_function_1', self, self.bad_function_1, ''))
        self.add_command(command.ExecCommand('execute bad_function_2', self, self.bad_function_1, ''))
        self.add_command(command.ExecCommand('execute bad_function_3', self, self.bad_function_1, ''))

    def bad_function_1(self):
        '''Not enough arguments'''
        self.last_state = 'entered bad function 1, should not be here!'

    def bad_function_2(self, arg1, arg2, arg3):
        '''Too many arguments needed'''
        self.last_state = 'entered bad function 2, should not be here!'

    def bad_function_3(self, line, mode):
        '''Raises some exception'''
        self.last_state = 'entered bad function 3, should not be here!'
        return 1 / 0
