from  sysadmintoolkit.builtinplugins import commandprompt
import __init__ as appinfo
import ConfigParser
import argparse
import signal
import sysadmintoolkit


if __name__ == '__main__':

    # ---- Arguments parsing

    # Parse arguments
    argparser = argparse.ArgumentParser(description='A system administrator\'s toolkit ')

    argparser.add_argument('-c', '--config_file', default='/etc/sysadmin-toolkit/sysadmin-toolkit.conf', \
                           help='Main configuration file', type=str, action='store')
    argparser.add_argument('cmd', help='Execute this command in the toolkit and exit', type=str, \
                           nargs='*')
    argparser.add_argument('--disable-shell', default=False, \
                           help='All user controlled shell interactions ("!","|") are disabled', action='store_true')
    argparser.add_argument('-q', '--quiet', default=False, \
                           help='Turn all possible debugging to off, only stdout from commands are displayed', action='store_true')
    argparser.add_argument('-d', '--debug', default=False, \
                           help='Turn all possible debugging to on', action='store_true')
    argparser.add_argument('-v', '--verbose', default=False, \
                           help='Increase logging level to INFO', action='store_true')
    argparser.add_argument('-V', '--version', action='version', \
                           version='%(prog)s ' + '%s' % appinfo.__version__)

    args = argparser.parse_args()

    if args.debug:
        print 'All debugging turned to ON'

    # ---- External and default configuration

    # Defaults
    defaults = {'enable-plugin': 'yes',
                'log-destination': 'console',
                'log-level': 'warning',
                'name-resolution': 'yes',
                }

    # Fill the config defaults with arguments
    override_logging_dest = None
    override_logging_level = None

    if args.quiet:
        override_logging_dest = 'null'

    if args.verbose:
        override_logging_level = 'info'
        override_logging_dest = 'console'

    if args.debug:
        override_logging_level = 'debug'
        override_logging_dest = 'console'

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

    # Make sure the commandprompt plugin will be loaded
    if 'commandprompt' not in config.sections():
        config.add_section('commandprompt')

    if not config.has_option('commandprompt', 'plugin-dir'):
        config.set('commandprompt', 'plugin-dir', '/etc/sysadmin-toolkit/plugin.d/')

    if not config.has_option('commandprompt', 'scripts-dir'):
        config.set('commandprompt', 'script-dir', '/etc/sysadmin-toolkit/scripts.d/')

    # Populate config with arguments
    sysadmintoolkit.utils.set_config_logging(config, override_logging_dest, override_logging_level)

    if args.debug:
        sysadmintoolkit.utils.print_config_contents(config)

    # ---- Initialize commandprompt logging
    CommandPromptLogger = sysadmintoolkit.utils.get_logger('commandprompt', dict(config.items('commandprompt')))
    CommandPromptLogger.debug("Started sysadmintoolkit/__main__.py")

    # ---- Load plugins and their instance
    sections = config.sections()
    sections.sort()

    for section in sections:
        try:
            pass
        except:
            pass

    PluginLogger = sysadmintoolkit.utils.get_logger('plugin.commandprompt', dict(config.items('commandprompt')))

    if PluginLogger is not None:
        cmdpromptplugin = commandprompt.CommandPrompt.get_plugin(dict(config.items('commandprompt')), PluginLogger)
    else:
        CommandPromptLogger.error('Could not initialize logger for %s' % 'commandprompt')

    # Instantiate the main command prompt at the correct mode
    admincmdprompt = sysadmintoolkit.cmdprompt.CmdPrompt(CommandPromptLogger, mode='admin', shell_allowed=not args.disable_shell)

    def SIGWINCH_handler(signum=None, frame=None):
        (height, width) = sysadmintoolkit.utils.get_terminal_size()
        admincmdprompt.update_window_size(width, height)

    # Refresh window size
    signal.signal(signal.SIGWINCH, SIGWINCH_handler)
    SIGWINCH_handler()

    # Add each plugin to the commandprompt
    admincmdprompt.add_plugin(cmdpromptplugin)

    # Loop on the main command or directly execute a command
    if len(args.cmd) is 0:
        admincmdprompt.cmdloop()
    else:
        admincmdprompt.preloop()

        for cmd in ' '.join(args.cmd).split(';'):
            admincmdprompt.onecmd(cmd)

        admincmdprompt.postloop()
