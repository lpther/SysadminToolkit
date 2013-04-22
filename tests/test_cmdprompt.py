import unittest
from sysadmintoolkit import exception, plugin, cmdprompt, logger

class CmdPromptTestCase(unittest.TestCase):
    '''Testing command module
    '''
    def setUp(self):
         pass

    def test_bad_instanciation_types(self):
         self.assertRaises(exception.CommandPromptError, cmdprompt.CmdPrompt, None)
         self.assertRaises(exception.CommandPromptError, cmdprompt.CmdPrompt, None, mode=None)

    def test_correct_instanciation(self):
        logger_ = logger.NullLogger('debug')

        self.assertTrue(cmdprompt.CmdPrompt(logger_, mode='testcase'))
