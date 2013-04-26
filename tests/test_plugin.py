from sysadmintoolkit import plugin, exception
import logging
import unittest


class PluginTestCase(unittest.TestCase):
    '''Testing command module
    '''
    def setUp(self):
        self.nulllogger = logging.getLogger('null')
        self.nulllogger.addHandler(logging.NullHandler())

    def test_bad_instanciation_types(self):
        self.assertRaises(exception.CommandPromptError, plugin.Plugin, None, None, None)

    def test_correct_instanciation(self):
        self.assertTrue(plugin.Plugin('testcase-plugin', self.nulllogger, None), None)

    def test_basic_properties_getters_setters(self):
        pluginname = 'testcase-plugin'

        testplugin = plugin.Plugin('testcase-plugin', self.nulllogger, None)

        self.assertEqual(pluginname, testplugin.get_name())
