from sysadmintoolkit import cmdprompt, builtinplugins
from  sysadmintoolkit.builtinplugins import commandprompt
import ConfigParser
import logging
import sys

if __name__ == '__main__':

    # Parse arguments

    ConsoleHandler = logging.StreamHandler(sys.stdout)
    ConsoleHandler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    NullHandler = logging.NullHandler()

    # Here the commandprompt logging should be done
    CommandPromptLogger = logging.getLogger('commandprompt')
    CommandPromptLogger.addHandler(ConsoleHandler)
    CommandPromptLogger.setLevel(logging.DEBUG)

    CommandPromptLogger.debug("Started sysadmintoolkit __main__.py")

    # Load the configuration file
    configParser = ConfigParser.SafeConfigParser()

    # Load appropriate plugins and instantiate them
    PluginLogger = logging.getLogger('plugin.%s' % 'commandprompt')
    PluginLogger.addHandler(ConsoleHandler)
    PluginLogger.setLevel(logging.DEBUG)

    cmdpromptplugin = commandprompt.CommandPrompt(PluginLogger)

    # Instantiate the main command prompt at the correct mode
    rootcmdprompt = cmdprompt.CmdPrompt(CommandPromptLogger, mode='root')

    # Add each plugin to the commandprompt
    rootcmdprompt.add_plugin(cmdpromptplugin)

    print rootcmdprompt.command_tree.get_subcmd_labels()

    # Loop on the main command
    rootcmdprompt.cmdloop()
