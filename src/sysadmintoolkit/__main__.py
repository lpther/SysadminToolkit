from  sysadmintoolkit.builtinplugins import commandprompt
import __init__ as appinfo
import ConfigParser
import argparse
import signal
import logging
import sys
import sysadmintoolkit


if __name__ == '__main__':

    # ---- Arguments parsing

    # Parse arguments
    argparser = argparse.ArgumentParser(description='A system administrator\'s toolkit ')

    argparser.add_argument('-c', '--config_file', default='/etc/sysadmin-toolkit/sysadmin-toolkit.conf', \
                           help='Main configuration file', type=str, action='store')
    argparser.add_argument('cmd', help='Execute this command in the toolkit and exit', type=str, \
                           nargs='*')
    argparser.add_argument('-d', '--debug', default=False, \
                           help='Turn all possible debugging to on', action='store_true')
    argparser.add_argument('-V', '--version', action='version', \
                           version='%(prog)s ' + '%s' % appinfo.__version__)

    args = argparser.parse_args()

    if args.debug:
        print 'All debugging turned to ON'

    # ---- External and default configuration

    # Defaults
    defaults = {'enable-plugin': 'yes',
                'log-destination': 'stdout',
                'log-level': 'warning',
                'name-resolution': 'yes',
                }

    # Verify and load the configuration file
    try:
        configfile = open(args.config_file, 'r')
        configfile.close()
    except:
        argparser.error('Configuration file could not be opened')

    try:
        config = ConfigParser.SafeConfigParser(defaults)
        config.read(args.config_file)
    except ConfigParser.Error as e:
        argparser.error('Configuration file could not be parsed:\n\n%s' % sysadmintoolkit.utils.indent_text(str(e)))

    if 'commandprompt' not in config.sections():
        config.add_section('commandprompt')

    if args.debug:
        sysadmintoolkit.utils.print_config_contents(config)

    # ---- Initialize logging

    ConsoleHandler = logging.StreamHandler(sys.stdout)
    ConsoleHandler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    NullHandler = logging.NullHandler()

    CommandPromptLogger = logging.getLogger('commandprompt')
    CommandPromptLogger.addHandler(ConsoleHandler)
    CommandPromptLogger.setLevel(logging.DEBUG)

    CommandPromptLogger.debug("Started sysadmintoolkit/__main__.py")

    # Load appropriate plugins and instantiate them
    PluginLogger = logging.getLogger('plugin.%s' % 'commandprompt')
    PluginLogger.addHandler(ConsoleHandler)
    PluginLogger.setLevel(logging.DEBUG)

    cmdpromptplugin = commandprompt.CommandPrompt(PluginLogger, config.items('commandprompt'))

    # Instantiate the main command prompt at the correct mode
    admincmdprompt = sysadmintoolkit.cmdprompt.CmdPrompt(CommandPromptLogger, mode='admin')

    def SIGWINCH_handler(signum=None, frame=None):
        (height, width) = sysadmintoolkit.utils.get_terminal_size()
        admincmdprompt.update_window_size(width, height)

    # Refresh window size
    signal.signal(signal.SIGWINCH, SIGWINCH_handler)
    SIGWINCH_handler()

    # Add each plugin to the commandprompt
    admincmdprompt.add_plugin(cmdpromptplugin)

    print admincmdprompt.command_tree.get_sub_keywords_labels()

    # Loop on the main command or directly execute a command
    if len(args.cmd) is 0:
        admincmdprompt.cmdloop()
    else:
        for cmd in ' '.join(args.cmd).split(';'):
            admincmdprompt.onecmd(cmd)
