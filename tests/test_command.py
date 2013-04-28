import unittest
import logging
import sysadmintoolkit


class CommandTestCase(unittest.TestCase):
    '''Testing command module
    '''
    def setUp(self):
        self.nulllogger = logging.getLogger('null')
        self.nulllogger.addHandler(logging.NullHandler())

     
    def test_bad_instantiation_types(self):
        self.assertRaises(sysadmintoolkit.exception.PluginError, sysadmintoolkit.command.ExecCommand, None, None, None)
        self.assertRaises(sysadmintoolkit.exception.PluginError, sysadmintoolkit.command.ExecCommand, 'this is a test case', None, None)
        self.assertRaises(sysadmintoolkit.exception.PluginError, sysadmintoolkit.command.ExecCommand, 'this is a test case', sysadmintoolkit.plugin.Plugin('testcase-plugin', self.nulllogger, None), None)

    def test_correct_instantiation(self):
        self.assertTrue(sysadmintoolkit.command.ExecCommand('this is a test case', sysadmintoolkit.plugin.Plugin('testcase-plugin', self.nulllogger, None), self.setUp))
