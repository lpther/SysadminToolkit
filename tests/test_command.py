from sysadmintoolkit import command, exception, plugin
import logging
import unittest

class CommandTestCase(unittest.TestCase):
    '''Testing command module
    '''
    def setUp(self):
        self.nulllogger = logging.getLogger('null')
        self.nulllogger.addHandler(logging.NullHandler())

     
    def test_bad_instanciation_types(self):
        self.assertRaises(exception.PluginError, command.Command, None, None, None)
        self.assertRaises(exception.PluginError, command.Command, 'this is a test case', None, None)
        self.assertRaises(exception.PluginError, command.Command, 'this is a test case', plugin.Plugin('testcase-plugin', self.nulllogger), None)

    def test_correct_instanciation(self):
        self.assertTrue(command.Command('this is a test case', plugin.Plugin('testcase-plugin', self.nulllogger), self.setUp))
