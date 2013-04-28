import unittest
import sysadmintoolkit
import logging


class PluginTestCase(unittest.TestCase):
    '''Testing command module
    '''
    def setUp(self):
        self.nulllogger = logging.getLogger('null')
        self.nulllogger.addHandler(logging.NullHandler())

    def test_bad_instantiation_types(self):
        self.assertRaises(sysadmintoolkit.exception.CommandPromptError, sysadmintoolkit.plugin.Plugin, None, None, None)

    def test_correct_instantiation(self):
        self.assertTrue(sysadmintoolkit.plugin.Plugin('testcase-plugin', self.nulllogger, None), None)

    def test_basic_properties_getters_setters(self):
        pluginname = 'testcase-plugin'

        testplugin = sysadmintoolkit.plugin.Plugin('testcase-plugin', self.nulllogger, None)

        self.assertEqual(pluginname, testplugin.get_name())
