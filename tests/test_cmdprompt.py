import sysadmintoolkit
import dummyplugin
import logging
import unittest
import sys
import os


class CmdPromptTestCase(unittest.TestCase):
    '''Testing commandprompt module
    '''
    def setUp(self):
        self.original_stdout = sys.stdout
        self.devnull = open(os.devnull, 'w')

        self.nulllogger = logging.getLogger('null')
        self.nulllogger.addHandler(logging.NullHandler())

        self.basicplugin = dummyplugin.DummyPlugin('dummyplugin')

    def test_bad_instantiation_types(self):
        self.assertRaises(sysadmintoolkit.exception.CommandPromptError, sysadmintoolkit.cmdprompt.CmdPrompt, None)
        self.assertRaises(sysadmintoolkit.exception.CommandPromptError, sysadmintoolkit.cmdprompt.CmdPrompt, None, mode=None)

    def test_correct_instantiation(self):
        self.assertTrue(sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase'))

    def test_add_plugin(self):
        cmd = sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase')

        cmd.add_plugin(self.basicplugin)

        self.assertTrue('dummyplugin' in cmd.command_tree.get_sub_keywords_labels())
        self.assertTrue('dummyplugin is ready' in cmd.command_tree.get_sub_keywords_labels())
        self.assertTrue(cmd.command_tree.get_sub_keywords_labels()['dummyplugin is ready']['help']['dummyplugin'].get_shorthelp() == 'shorthelp for dummyplugin is ready')

    def test_execute_commands_ok(self):
        # cmd = sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase')
        pass

    def test_execute_commands_with_errors(self):
        badplugin = dummyplugin.BadPlugin('badplugin')

        cmd = sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase', is_interactive=False)
        cmd.add_plugin(badplugin)

        cmd.preloop()

        try:
            sys.stdout = self.devnull
            self.assertEqual(cmd.onecmd('execute bad_function_1'), 401)
            self.assertEqual(badplugin.last_state, 'init')

            self.assertEqual(cmd.onecmd('execute bad_function_2'), 401)
            self.assertEqual(badplugin.last_state, 'init')

            self.assertEqual(cmd.onecmd('execute bad_function_3'), 401)
            self.assertEqual(badplugin.last_state, 'init')
        finally:
            sys.stdout = self.original_stdout

    def test_execute_static_commands(self):
        behavedplugin1 = dummyplugin.BehavedPlugin('behavedplugin1')
        behavedplugin2 = dummyplugin.BehavedPlugin('behavedplugin2')

        cmd = sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase', is_interactive=False)
        cmd.add_plugin(behavedplugin1)
        cmd.add_plugin(behavedplugin2)

        cmd.preloop()

        try:
            sys.stdout = self.devnull
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('unique behavedplugin1 command'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behavedplugin1 behaved function 1')
            self.assertEqual(cmd.onecmd('reset'), 0)

            self.assertEqual(cmd.onecmd('    unique      behavedplugin1     command     with       spaces    '), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behavedplugin1 behaved function 1')
            self.assertEqual(cmd.onecmd('reset'), 0)

            self.assertEqual(cmd.onecmd('conflicting command'), 403)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('non conflicting command'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behavedplugin1 behaved function 1')
            self.assertEqual(behavedplugin2.last_state, 'plugin behavedplugin2 behaved function 1')
            self.assertEqual(cmd.onecmd('reset'), 0)
        finally:
            sys.stdout = self.original_stdout

    def test_execute_static_commands_with_autocompletion(self):
        behavedplugin1 = dummyplugin.BehavedPlugin('behavedplugin1')
        behavedplugin2 = dummyplugin.BehavedPlugin('behavedplugin2')

        cmd = sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase', is_interactive=False)
        cmd.add_plugin(behavedplugin1)
        cmd.add_plugin(behavedplugin2)

        cmd.preloop()

        try:
            sys.stdout = self.devnull
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('uniq behavedplugin1 c'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behavedplugin1 behaved function 1')
            self.assertEqual(cmd.onecmd('reset'), 0)

            self.assertEqual(cmd.onecmd('    uniq      behavedplugin1     command     w       spaces    '), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behavedplugin1 behaved function 1')
            self.assertEqual(cmd.onecmd('reset'), 0)

            self.assertEqual(cmd.onecmd('co c'), 403)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('uni command'), 404)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('n conflict command'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behavedplugin1 behaved function 1')
            self.assertEqual(behavedplugin2.last_state, 'plugin behavedplugin2 behaved function 1')
            self.assertEqual(cmd.onecmd('reset'), 0)
        finally:
            sys.stdout = self.original_stdout

    def test_execute_non_exec_commands(self):
        behavedplugin1 = dummyplugin.BehavedPlugin('behavedplugin1')
        behavedplugin2 = dummyplugin.BehavedPlugin('behavedplugin2')

        cmd = sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase', is_interactive=False)
        cmd.add_plugin(behavedplugin1)
        cmd.add_plugin(behavedplugin2)

        cmd.preloop()

        try:
            sys.stdout = self.devnull

            self.assertEqual(cmd.onecmd('non existing command'), 411)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            # Test a registered label with no executable commands
            self.assertEqual(cmd.onecmd('unique'), 410)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('this is just a help label'), 410)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')
        finally:
            sys.stdout = self.original_stdout

    def test_execute_non_exec_commands_with_autocompletion(self):
        behavedplugin1 = dummyplugin.BehavedPlugin('behavedplugin1')
        behavedplugin2 = dummyplugin.BehavedPlugin('behavedplugin2')

        cmd = sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase', is_interactive=False)
        cmd.add_plugin(behavedplugin1)
        cmd.add_plugin(behavedplugin2)

        cmd.preloop()

        try:
            sys.stdout = self.devnull

            self.assertEqual(cmd.onecmd('non ex co'), 411)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            # Test a registered label with no executable commands
            self.assertEqual(cmd.onecmd('uniq'), 410)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('th i j a he labe'), 410)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')
        finally:
            sys.stdout = self.original_stdout

    def test_execute_dynamic_commands(self):
        behavedplugin1 = dummyplugin.BehavedDynamicPlugin('behaveddynamicplugin1')
        behavedplugin2 = dummyplugin.BehavedDynamicPlugin('behaveddynamicplugin2')

        cmd = sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase', is_interactive=False)
        cmd.add_plugin(behavedplugin1)
        cmd.add_plugin(behavedplugin2)

        cmd.preloop()

        try:
            sys.stdout = self.devnull
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('unique behaveddynamicplugin1 apple command'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behaveddynamicplugin1 behaved function 1')
            self.assertEqual(behavedplugin1.dyn_command_line, 'unique behaveddynamicplugin1 apple command')
            self.assertEqual(cmd.onecmd('reset'), 0)

            self.assertEqual(cmd.onecmd('unique behaveddynamicplugin1 apple command apricot'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behaveddynamicplugin1 behaved function 1')
            self.assertEqual(behavedplugin1.dyn_command_line, 'unique behaveddynamicplugin1 apple command apricot')
            self.assertEqual(cmd.onecmd('reset'), 0)

            self.assertEqual(cmd.onecmd('conflicting apple command'), 403)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('conflicting apple command apricot'), 403)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('non conflicting apple command'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behaveddynamicplugin1 behaved function 1')
            self.assertEqual(behavedplugin2.last_state, 'plugin behaveddynamicplugin2 behaved function 1')
            self.assertEqual(behavedplugin1.dyn_command_line, 'non conflicting apple command')
            self.assertEqual(behavedplugin2.dyn_command_line, 'non conflicting apple command')
            self.assertEqual(cmd.onecmd('reset'), 0)

            self.assertEqual(cmd.onecmd('non conflicting apple command apricot'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behaveddynamicplugin1 behaved function 1')
            self.assertEqual(behavedplugin2.last_state, 'plugin behaveddynamicplugin2 behaved function 1')
            self.assertEqual(behavedplugin1.dyn_command_line, 'non conflicting apple command apricot')
            self.assertEqual(behavedplugin2.dyn_command_line, 'non conflicting apple command apricot')
            self.assertEqual(cmd.onecmd('reset'), 0)

            # Test a registered dynamic label with no executable commands
            self.assertEqual(cmd.onecmd('non conflicting apple'), 410)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')
        finally:
            sys.stdout = self.original_stdout

    def test_execute_dynamic_commands_with_autocompletion(self):
        behavedplugin1 = dummyplugin.BehavedDynamicPlugin('behaveddynamicplugin1')
        behavedplugin2 = dummyplugin.BehavedDynamicPlugin('behaveddynamicplugin2')

        cmd = sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase', is_interactive=False)
        cmd.add_plugin(behavedplugin1)
        cmd.add_plugin(behavedplugin2)

        cmd.preloop()

        try:
            sys.stdout = self.devnull
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('uniq behaveddynamicplugin1 app comm'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behaveddynamicplugin1 behaved function 1')
            self.assertEqual(behavedplugin1.dyn_command_line, 'unique behaveddynamicplugin1 apple command')
            self.assertEqual(cmd.onecmd('reset'), 0)

            self.assertEqual(cmd.onecmd('uniq behaveddynamicplugin1 appl command apr'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behaveddynamicplugin1 behaved function 1')
            self.assertEqual(behavedplugin1.dyn_command_line, 'unique behaveddynamicplugin1 apple command apricot')
            self.assertEqual(cmd.onecmd('reset'), 0)

            self.assertEqual(cmd.onecmd('conflicting app command'), 403)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('conflicting app command apricot'), 403)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('non conflicting app command'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behaveddynamicplugin1 behaved function 1')
            self.assertEqual(behavedplugin2.last_state, 'plugin behaveddynamicplugin2 behaved function 1')
            self.assertEqual(behavedplugin1.dyn_command_line, 'non conflicting apple command')
            self.assertEqual(behavedplugin2.dyn_command_line, 'non conflicting apple command')
            self.assertEqual(cmd.onecmd('reset'), 0)

            self.assertEqual(cmd.onecmd('non conflicting app command apricot'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behaveddynamicplugin1 behaved function 1')
            self.assertEqual(behavedplugin2.last_state, 'plugin behaveddynamicplugin2 behaved function 1')
            self.assertEqual(behavedplugin1.dyn_command_line, 'non conflicting apple command apricot')
            self.assertEqual(behavedplugin2.dyn_command_line, 'non conflicting apple command apricot')
            self.assertEqual(cmd.onecmd('reset'), 0)

            # Test a registered dynamic label with no executable commands
            self.assertEqual(cmd.onecmd('non conflicting app'), 410)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')
        finally:
            sys.stdout = self.original_stdout

    def test_execute_dynamic_commands_different_dyn_keyword_types(self):
        behavedplugin1 = dummyplugin.BehavedDynamicPlugin('behaveddynamicplugin1')
        behavedplugin2 = dummyplugin.BehavedDynamicPlugin_2('behaveddynamicplugin2')

        cmd = sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase', is_interactive=False)
        cmd.add_plugin(behavedplugin1)
        cmd.add_plugin(behavedplugin2)

        cmd.preloop()

        try:
            sys.stdout = self.devnull

            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('uni command'), 404)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')

            self.assertEqual(cmd.onecmd('non conflicting potato command'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'plugin behaveddynamicplugin2 behaved function 1')
            self.assertEqual(behavedplugin2.dyn_command_line, 'non conflicting potato command')
            self.assertEqual(cmd.onecmd('reset'), 0)

            self.assertEqual(cmd.onecmd('non conflicting banana command'), 12345)
            self.assertEqual(behavedplugin1.last_state, 'plugin behaveddynamicplugin1 behaved function 1')
            self.assertEqual(behavedplugin2.last_state, 'plugin behaveddynamicplugin2 behaved function 1')
            self.assertEqual(behavedplugin1.dyn_command_line, 'non conflicting banana command')
            self.assertEqual(behavedplugin2.dyn_command_line, 'non conflicting banana command')
            self.assertEqual(cmd.onecmd('reset'), 0)

            self.assertEqual(cmd.onecmd('non conflicting p command'), 404)
            self.assertEqual(behavedplugin1.last_state, 'init')
            self.assertEqual(behavedplugin2.last_state, 'init')
            self.assertEqual(cmd.onecmd('reset'), 0)

        finally:
            sys.stdout = self.original_stdout

    def test_command_analysis(self):
        behavedplugin1 = dummyplugin.BehavedPlugin('behavedplugin1')

        cmd = sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase', is_interactive=False)
        cmd.add_plugin(behavedplugin1)

        cmd.preloop()

        self.assertTrue('exec_commands' in sysadmintoolkit.cmdprompt._UserInput('unique behavedplugin1 command', cmd).status)
        self.assertTrue('exec_commands_with_pipe' in sysadmintoolkit.cmdprompt._UserInput('unique behavedplugin1 command | some shell command', cmd).status)
        self.assertTrue('some shell command' in sysadmintoolkit.cmdprompt._UserInput('unique behavedplugin1 command | some shell command', cmd).rest_of_line)
