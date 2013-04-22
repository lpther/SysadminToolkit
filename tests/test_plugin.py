import unittest
from sysadmintoolkit import plugin, exception

class PluginTestCase(unittest.TestCase):
    '''Testing command module
    '''
    def setUp(self):
         pass

    def test_bad_instanciation_types(self):
        self.assertRaises(exception.CommandPromptError, plugin.Plugin, None)

    def test_correct_instanciation(self):
        self.assertTrue(plugin.Plugin('testcase-plugin'), None)

    def test_basic_properties_getters_setters(self):
        pluginname = 'testcase-plugin'

        testplugin = plugin.Plugin('testcase-plugin')

        self.assertEqual(pluginname, testplugin.get_name())
