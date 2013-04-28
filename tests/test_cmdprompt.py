import sysadmintoolkit
import logging
import unittest


class CmdPromptTestCase(unittest.TestCase):
    '''Testing commandprompt module
    '''
    def setUp(self):
        self.nulllogger = logging.getLogger('null')
        self.nulllogger.addHandler(logging.NullHandler())

        self.commandpromptplugin = sysadmintoolkit.builtinplugins.commandprompt.CommandPrompt(self.nulllogger, None)

    def test_bad_instantiation_types(self):
         self.assertRaises(sysadmintoolkit.exception.CommandPromptError, sysadmintoolkit.cmdprompt.CmdPrompt, None)
         self.assertRaises(sysadmintoolkit.exception.CommandPromptError, sysadmintoolkit.cmdprompt.CmdPrompt, None, mode=None)

    def test_correct_instantiation(self):
        self.assertTrue(sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase'))

    def test_add_plugin(self):
        cmd = sysadmintoolkit.cmdprompt.CmdPrompt(self.nulllogger, mode='testcase')

        cmd.add_plugin(self.commandpromptplugin)

        self.assertTrue('debug' in cmd.command_tree.get_sub_keywords_labels(), True)
        self.assertTrue('debug commandprompt' in cmd.command_tree.get_sub_keywords_labels(), True)
