from sysadmintoolkit import command, exception, plugin
import logging
import unittest

class CommandTestCase(unittest.TestCase):
    '''Testing command module
    '''
    def setUp(self):
        self.nulllogger = logging.getLogger('null')
        self.nulllogger.addHandler(logging.NullHandler())

     
    def test_bad_instantiation_types(self):
        self.assertRaises(exception.PluginError, command.ExecCommand, None, None, None)
        self.assertRaises(exception.PluginError, command.ExecCommand, 'this is a test case', None, None)
        self.assertRaises(exception.PluginError, command.ExecCommand, 'this is a test case', plugin.Plugin('testcase-plugin', self.nulllogger, None), None)

    def test_correct_instantiation(self):
        self.assertTrue(command.ExecCommand('this is a test case', plugin.Plugin('testcase-plugin', self.nulllogger, None), self.setUp))
