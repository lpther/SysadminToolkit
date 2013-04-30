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
        finally:
            sys.stdout = self.original_stdout
