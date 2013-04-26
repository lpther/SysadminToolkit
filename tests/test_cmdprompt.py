from sysadmintoolkit import exception, plugin, cmdprompt, builtinplugins
from  sysadmintoolkit.builtinplugins import commandprompt
import logging
import unittest


class CmdPromptTestCase(unittest.TestCase):
    '''Testing commandprompt module
    '''
    def setUp(self):
        self.nulllogger = logging.getLogger('null')
        self.nulllogger.addHandler(logging.NullHandler())

        self.commandpromptplugin = commandprompt.CommandPrompt(self.nulllogger, None)

    def test_bad_instanciation_types(self):
         self.assertRaises(exception.CommandPromptError, cmdprompt.CmdPrompt, None)
         self.assertRaises(exception.CommandPromptError, cmdprompt.CmdPrompt, None, mode=None)

    def test_correct_instanciation(self):
        self.assertTrue(cmdprompt.CmdPrompt(self.nulllogger, mode='testcase'))

    def test_add_plugin(self):
        cmd = cmdprompt.CmdPrompt(self.nulllogger, mode='testcase')

        cmd.add_plugin(self.commandpromptplugin)

        self.assertTrue('debug' in cmd.command_tree.get_sub_keywords_labels(), True)
        self.assertTrue('debug commandprompt' in cmd.command_tree.get_sub_keywords_labels(), True)
