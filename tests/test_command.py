import unittest
from sysadmintoolkit import command, exception, plugin

class CommandTestCase(unittest.TestCase):
    '''Testing command module
    '''
    def setUp(self):
         pass
     
    def test_bad_instanciation_types(self):
         self.assertRaises(exception.PluginError, command.Command, None, None, None)
         self.assertRaises(exception.PluginError, command.Command, 'this is a test case', None, None)
         self.assertRaises(exception.PluginError, command.Command, 'this is a test case', plugin.Plugin('testcase-plugin'), None)

    def test_correct_instanciation(self):
        def f():
            pass
        
        self.assertTrue(command.Command('this is a test case', plugin.Plugin('testcase-plugin'), f))
