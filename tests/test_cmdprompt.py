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

        self.badplugin = dummyplugin.BadPlugin('badplugin')

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
        cmd = sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase', is_interactive=False)
        cmd.add_plugin(self.badplugin)

        cmd.preloop()

        try:
            sys.stdout = self.devnull
            self.assertEqual(cmd.onecmd('execute bad_function_1'), 401)
            self.assertEqual(self.badplugin.last_state, 'init')

            self.assertEqual(cmd.onecmd('execute bad_function_2'), 401)
            self.assertEqual(self.badplugin.last_state, 'init')

            self.assertEqual(cmd.onecmd('execute bad_function_3'), 401)
            self.assertEqual(self.badplugin.last_state, 'init')
        finally:
            sys.stdout = self.original_stdout
