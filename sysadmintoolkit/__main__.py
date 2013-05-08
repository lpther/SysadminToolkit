import __init__ as appinfo
import ConfigParser
import argparse
import signal
import sysadmintoolkit
import sys
import os


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

    # Verify and load the configuration file
    try:
        configfile = open(args.config_file, 'r')
        configfile.close()
    except:
        argparser.error('Configuration file could not be opened')

    try:
        config = ConfigParser.SafeConfigParser()
        config.read(args.config_file)

        for default in defaults:
            if default not in dict(config.items('DEFAULT')):
                config.set('DEFAULT', default, defaults[default])

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
    # Fill the config defaults with arguments
    override_logging_dest = None
    override_logging_level = None

    if args.quiet:
        sysadmintoolkit.utils.override_config(config, 'log-destination', 'null')

    if args.verbose:
        sysadmintoolkit.utils.override_config(config, 'log-level', 'info')
        sysadmintoolkit.utils.override_config(config, 'log-destination', 'console')

    if args.debug:
        sysadmintoolkit.utils.override_config(config, 'log-level', 'debug')
        sysadmintoolkit.utils.override_config(config, 'log-destination', 'console')

    # ---- Initialize commandprompt logging
    CommandPromptLogger = sysadmintoolkit.utils.get_logger('commandprompt', dict(config.items('commandprompt')))
    CommandPromptLogger.debug("Started %s" % sys.executable)

    sysadmintoolkit.utils.print_config_contents(config, CommandPromptLogger)

    # ---- Load plugins and their instance
    plugin_set = sysadmintoolkit.utils.get_plugins_from_config(config, config.get('commandprompt', 'plugin-dir'), CommandPromptLogger, ['commandprompt'])

    # ---- Instantiate the main command prompt at the correct mode
    if os.getuid() is 0:
        initial_cmdprompt = sysadmintoolkit.cmdprompt.CmdPrompt(CommandPromptLogger, mode='root', \
                                                         shell_allowed=not args.disable_shell, is_interactive=len(args.cmd) is 0)
    else:
        initial_cmdprompt = sysadmintoolkit.cmdprompt.CmdPrompt(CommandPromptLogger, mode='operator', \
                                                         shell_allowed=not args.disable_shell, is_interactive=len(args.cmd) is 0)

    # ---- Handle window resizing
    def SIGWINCH_handler(signum=None, frame=None):
        (height, width) = sysadmintoolkit.utils.get_terminal_size()
        initial_cmdprompt.update_window_size(width, height)

    signal.signal(signal.SIGWINCH, SIGWINCH_handler)
    SIGWINCH_handler()

    # Update pluginset for all plugins and add to the commandprompt
    for plugin in plugin_set.get_plugins():
        plugin_set.get_plugins()[plugin].update_plugin_set(plugin_set)
        initial_cmdprompt.add_plugin(plugin_set.get_plugins()[plugin])

    # Loop on the main command or directly execute a command
    if len(args.cmd) is 0:
        initial_cmdprompt.cmdloop()
    else:
        initial_cmdprompt.preloop()

        for cmd in ' '.join(args.cmd).split(';'):
            initial_cmdprompt.onecmd(cmd)

        initial_cmdprompt.postloop()
