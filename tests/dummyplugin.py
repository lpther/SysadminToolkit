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

        self.add_command(command.ExecCommand('execute bad_function_1', self, self.bad_function_1))
        self.add_command(command.ExecCommand('execute bad_function_2', self, self.bad_function_2))
        self.add_command(command.ExecCommand('execute bad_function_3', self, self.bad_function_3))

    def bad_function_1(self):
        '''Not enough arguments'''
        self.last_state = 'entered bad function 1, should not be here!'

    def bad_function_2(self, arg1, arg2, arg3):
        '''Too many arguments needed'''
        self.last_state = 'entered bad function 2, should not be here!'

    def bad_function_3(self, user_input_obj):
        '''Raises some exception'''
        print 'Entered bad function 3 !'
        return 1 / 0


class BehavedPlugin(DummyPlugin):
    def __init__(self, name):
        super(BehavedPlugin, self).__init__(name)

        self.add_command(command.ExecCommand('conflicting command', self, self.behaved_function_1))
        self.add_command(command.ExecCommand('non conflicting command', self, self.behaved_function_1, allow_conflict=True))
        self.add_command(command.ExecCommand('unique %s command' % self.name, self, self.behaved_function_1))
        self.add_command(command.ExecCommand('universal %s command' % self.name, self, self.behaved_function_1))
        self.add_command(command.ExecCommand('unique %s command    with spaces' % self.name, self, self.behaved_function_1))
        self.add_command(command.ExecCommand('reset', self, self.reset_state, allow_conflict=True))

        self.add_command(command.LabelHelp('this is just a help label', self, 'This label cannot be executed'))

    def behaved_function_1(self, user_input_obj):
        self.last_state = 'plugin %s behaved function 1' % self.name
        return 12345

    def reset_state(self, user_input_obj):
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

    def behaved_function_1(self, user_input_obj):
        self.last_state = 'plugin %s behaved function 1' % self.name
        self.dyn_command_line = user_input_obj.get_entered_command()
        return 12345

    def resolve_dynamic_keyword(self, user_input_obj):
        return {'apple': 'This is a green or red fruit', \
                'banana': 'This is a yellow fruit', \
                'apricot': 'This is an orange fruit', \
                'pineapple': 'This is an orange and yellow fruit', \
                }

    def reset_state(self, user_input_obj):
        self.last_state = 'init'


class BehavedDynamicPlugin_2(DummyPlugin):
    def __init__(self, name):
        super(BehavedDynamicPlugin_2, self).__init__(name)

        self.add_command(command.ExecCommand('non conflicting <fruit> command', self, self.behaved_function_1, allow_conflict=True))
        self.add_command(command.ExecCommand('conflicting <fruit> command', self, self.behaved_function_1))
        self.add_command(command.ExecCommand('non conflicting <vegetable> command', self, self.behaved_function_1, allow_conflict=True))
        self.add_command(command.ExecCommand('conflicting <vegetable> command', self, self.behaved_function_1))
        self.add_command(command.ExecCommand('universal %s command' % self.name, self, self.behaved_function_1))

        self.add_command(command.ExecCommand('reset', self, self.reset_state, allow_conflict=True))

        self.add_dynamic_keyword_fn('<fruit>', self.resolve_dynamic_keyword)
        self.add_dynamic_keyword_fn('<vegetable>', self.resolve_dynamic_keyword_2)

        self.dyn_command_line = ''

    def behaved_function_1(self, user_input_obj):
        self.last_state = 'plugin %s behaved function 1' % self.name
        self.dyn_command_line = user_input_obj.get_entered_command()
        return 12345

    def resolve_dynamic_keyword(self, user_input_obj):
        return {'orange': 'This is a orange fruit', \
                'banana': 'This is a yellow fruit', \
                }

    def resolve_dynamic_keyword_2(self, user_input_obj):
        return {'potato': 'This is an brownish vegetable', \
                'carrot': 'This is an orange vegetable', \
                }

    def reset_state(self, user_input_obj):
        self.last_state = 'init'


class BehavedReadlineFriendlyDynamicPlugin(DummyPlugin):
    '''
    Testing of autocompletion. Readline does not implement a way to clear buffer content.

    We can only "add" to the buffer. This will insert one command to test cases.
    '''
    def __init__(self, name):
        super(BehavedReadlineFriendlyDynamicPlugin, self).__init__(name)

        self.add_command(command.ExecCommand('unique <fruit> command <fruit>', self, self.behaved_function_1))
        self.add_command(command.ExecCommand('universal <fruit> command', self, self.behaved_function_1))

        self.add_dynamic_keyword_fn('<fruit>', self.resolve_dynamic_keyword)

        self.dyn_command_line = ''

    def behaved_function_1(self, user_input_obj):
        self.last_state = 'plugin %s behaved function 1' % self.name
        self.dyn_command_line = user_input_obj.get_entered_command()
        return 12345

    def resolve_dynamic_keyword(self, user_input_obj):
        return {'apple': 'This is a green or red fruit', \
                'banana': 'This is a yellow fruit', \
                'apricot': 'This is an orange fruit', \
                'pineapple': 'This is an orange and yellow fruit', \
                }

    def reset_state(self, user_input_obj):
        self.last_state = 'init'
