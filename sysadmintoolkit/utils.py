import os
import textwrap
import sys
import termios
import fcntl
import struct
import logging
import imp
import subprocess
import socket


def get_terminal_size(fd=1):
    """
    Returns height and width of current terminal. First tries to get
    size via termios.TIOCGWINSZ, then from environment. Defaults to 25
    lines x 80 columns if both methods fail.

    :param fd: file descriptor (default: 1=stdout)

    Taken from:
        http://blog.taz.net.au/2012/04/09/getting-the-terminal-size-in-python/
    """
    try:
        hw = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))

        if not isinstance(hw[0], int) or not isinstance(hw[1], int):
            hw = (25, 80)

    except:

        try:
            hw = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            hw = (25, 80)

    return hw


def get_status_output(shellcmd):
    '''
    Executes the provided shellcmd in a shell, and returns (return_code, output)

    stderr is interleaved in the returned output
    '''
    try:
        output = subprocess.check_output(shellcmd, shell=True, stderr=subprocess.STDOUT)
        return 0, output
    except Exception as e:
        return e.returncode, e.output


def indent_text(text, indent=2, width=80, keep_newline=True):
    '''
    Indents a string by indent spaces
    '''
    if not keep_newline:
        return textwrap.fill(text, width=width, initial_indent=" " * indent, subsequent_indent=" " * indent)
    else:
        out = ''
        for line in text.splitlines():
            out += textwrap.fill(line, width=width, initial_indent=" " * indent, subsequent_indent=" " * indent) + '\n'

        return out


def print_text_blocks(blocks):
    '''
    block    [{'str':str,
               'window_ratio':float,
               'maxwidth':int,
               'wrap':bool}]
    Prints the str for a ratio of window size, without
    exceeding maxwidth.

    If wrap is false, the text is no wrapped (and mess up the pretty output)
    (textwrap cannot parse colors). Wrap is not mandatory.
    '''
    window_width = get_terminal_size()[1]

    vertical_blocks = []
    vertical_blocks_len = []

    for block in blocks:
        blockstr, window_ratio, maxwidth = block['str'], block['window_ratio'], block['maxwidth']

        width = min(int(window_width * window_ratio), int(maxwidth))

        if 'wrap' in block and not block['wrap']:
        # The best thing would be to wrap a string while preserving the ascii colors
            uncolored_blockstr = ansi_color_stripper(blockstr)
            vertical_blocks += [([blockstr], width)]
            vertical_blocks_len += [1]
        else:
            vertical_blocks += [(textwrap.wrap(blockstr, width=width), width)]
            vertical_blocks_len += [len(textwrap.wrap(blockstr, width=width))]

    for index in range(max(vertical_blocks_len)):
        for vertical_block in vertical_blocks:
            (blockstr, width) = vertical_block

            if len(blockstr) > index:
                # Remove ansi color chars as they mess up string lengths
                uncolored_blockstr = ansi_color_stripper(blockstr[index])
                nb_ansi_color_chars = blockstr[index].count('\x1b') * 4

                if not nb_ansi_color_chars:
                    print blockstr[index].ljust(width),
                else:
                    # FIXME: Until textwrap/ljust words with ascii colors
                    print blockstr[index] + (' ' * (width - len(uncolored_blockstr))),
            else:
                print ' ' * width,

        print


def get_reversed_text(text):
    return '\033[7m' + text + '\033[0m'


def get_bold_text(text):
    return '\033[1m' + text + '\033[0m'


def get_underline_text(text):
    return '\033[4m' + text + '\033[0m'


def get_dark_text(text):
    return '\033[2m' + text + '\033[0m'


def get_grey_text(text):
    return '\033[37m' + text + '\033[0m'


def get_green_text(text):
    return '\033[92m' + text + '\033[0m'


def get_red_text(text):
    return '\033[91m' + text + '\033[0m'


def get_l4_portname(port, proto='tcp'):
    name = 'unknown'

    try:
        name = socket.getservbyport(port, proto)
    except:
        pass

    return name


def is_ipv4_addr(inputstr):
    from pyparsing import Combine, Word, nums

    ipAddress = Combine(Word(nums) + ('.' + Word(nums)) * 3)

    try:
        ipAddress.parseString(inputstr)
        return True
    except:
        return False


def get_hexstr_from_ipv4_addr(ipv4addr):
    try:
        octetlist = []
        for octetstr in ipv4addr.split('.'):
            octetlist.append(hex(int(octetstr))[2:].upper().zfill(2))

        return ''.join(octetlist)
    except:
        return None


def get_hexstr_from_l4_port(l4port):
    try:
        return hex(int(l4port))[2:].upper().zfill(4)
    except:
        return None


def print_config_contents(config, logger):
    logger.debug('External and default configuration loaded')
    logger.debug('')
    width = 100

    sections = config.sections()
    sections.sort()

    for section in sections:
        logger.debug('  Section %s' % section)
        logger.debug('    %s %s' % ('Option'.ljust(int(width * 0.5)), 'Value'))
        logger.debug('    %s %s' % ('------'.ljust(int(width * 0.5)), '-----'))

        options = config.options(section)
        options.sort()

        for option in options:
            value = config.get(section, option)
            logger.debug('    %s %s' % (option.ljust(int(width * 0.5)), value))

        logger.debug('')


def get_matching_prefix(prefix, possibilities):
    '''
    Returns the possibilities that match the prefix

    possibilities     list of str
    prefix            str
    '''
    if len(possibilities) is 0:
        return []
    else:
        return [p for p in possibilities if p.startswith(prefix)]


def get_logging_level(strlevel):
    '''
    Returns the correct logging level (from package)

    None if invalid level

    '''
    strlevel = strlevel.upper().strip()

    levels = {'DEBUG': logging.DEBUG,
              'INFO': logging.INFO,
              'WARNING': logging.WARNING,
              'ERROR': logging.ERROR,
              'CRITICAL': logging.CRITICAL}

    if strlevel in levels:
        return levels[strlevel]
    else:
        return None


def get_logging_type(strtype):
    strtype = strtype.lower().strip().split(':')[0]

    types = ['console', 'syslog', 'file', 'null']

    if strtype in types:
        return strtype
    else:
        return None


def get_syslog_facility(strfacility):
    '''
    Returns the correct logging facility (from package)

    None if invalid facility

    '''
    strfacility = strfacility.lower().strip()

    facilities = {'auth': logging.handlers.SysLogHandler.LOG_AUTH,
                  'authpriv': logging.handlers.SysLogHandler.LOG_AUTHPRIV,
                  'cron': logging.handlers.SysLogHandler.LOG_CRON,
                  'daemon': logging.handlers.SysLogHandler.LOG_DAEMON,
                  'ftp': logging.handlers.SysLogHandler.LOG_FTP,
                  'kern': logging.handlers.SysLogHandler.LOG_KERN,
                  'lpr': logging.handlers.SysLogHandler.LOG_LPR,
                  'mail': logging.handlers.SysLogHandler.LOG_MAIL,
                  'news': logging.handlers.SysLogHandler.LOG_NEWS,
                  'syslog': logging.handlers.SysLogHandler.LOG_SYSLOG,
                  'user': logging.handlers.SysLogHandler.LOG_USER,
                  'uucp': logging.handlers.SysLogHandler.LOG_UUCP,
                  'local0': logging.handlers.SysLogHandler.LOG_LOCAL0,
                  'local1': logging.handlers.SysLogHandler.LOG_LOCAL1,
                  'local2': logging.handlers.SysLogHandler.LOG_LOCAL2,
                  'local3': logging.handlers.SysLogHandler.LOG_LOCAL3,
                  'local4': logging.handlers.SysLogHandler.LOG_LOCAL4,
                  'local5': logging.handlers.SysLogHandler.LOG_LOCAL5,
                  'local6': logging.handlers.SysLogHandler.LOG_LOCAL6,
                  'local7': logging.handlers.SysLogHandler.LOG_LOCAL7,
                  }

    if strfacility in facilities:
        return facilities[strfacility]
    else:
        return None


def override_config(config, attr, value):
    '''
    Set the attribute to a specified value for all sections in the config.

    config         ConfigParser     config object
    attr, value    str
    '''
    for section in config.sections():
            config.set(section, attr, value)


def get_plugins_from_config(config, plugindir, logger, first_plugins=[]):
    '''
    Returns a pluginset containing all loadable plugins.

    config        ConfigParser.ConfigParser
    plugindir     str
    logger        logging.Logger
    first_plugins [str]
    '''
    import sysadmintoolkit

    plugin_set = sysadmintoolkit.plugin.PluginSet()

    for plugin in first_plugins:
        if plugin in config.sections():
            logger.debug('Loading plugin %s in priority' % plugin)

            try:
                module = get_python_module(plugin, plugindir, logger)
            except Exception as e:
                logger.error('Error loading plugin %s: %s' % (plugin, e))
                continue

            try:
                module_logger = get_logger('plugin.%s' % plugin, dict(config.items(plugin)), logger)

                plugin_set.add_plugin(module.get_plugin(module_logger, dict(config.items(plugin))))
                logger.info('Loaded plugin %s successfully' % plugin)
            except Exception as e:
                pass

    for plugin in config.sections():
        if plugin not in first_plugins:
            logger.debug('Loading plugin %s' % plugin)

            try:
                module = get_python_module(plugin, plugindir, logger)
            except Exception as e:
                logger.error('Error loading plugin %s: %s' % (plugin, e))
                continue

            try:
                module_logger = get_logger('plugin.%s' % plugin, dict(config.items(plugin)), logger)

                plugin_set.add_plugin(module.get_plugin(module_logger, dict(config.items(plugin))))
                logger.info('Loaded plugin %s successfully' % plugin)
            except Exception as e:
                logger.error('Error loading plugin %s: Python module loaded successfully but get_plugin() failed' % plugin)
                logger.debug('Full error: %s' % e)

    return plugin_set


def get_python_module(plugin, plugindir, logger):
    '''
    '''
    sysadmin_toolkit_module = imp.load_module("sysadmin_toolkit_module", \
                                              imp.find_module('sysadmintoolkit')[0], \
                                              imp.find_module('sysadmintoolkit')[1], \
                                              imp.find_module('sysadmintoolkit')[2])

    plugin_module = None
    module_file = None

    try:
        module_file, pathname, description = imp.find_module(plugin, ['%s/builtinplugins/' % sysadmin_toolkit_module.__path__[0]])

        plugin_module = imp.load_module('runtimeplugins_%s' % plugin, module_file, pathname, description)

        logger.debug('Built-in plugin %s loaded successfully' % plugin)

    except ImportError:
        # Module was not found in the builtinplugins
        pass
    finally:
        if module_file is not None:
            module_file.close()

    if plugin_module is None:
        try:
            module_file, pathname, description = imp.find_module(plugin, [plugindir])

            plugin_module = imp.load_module('runtimeplugins_%s' % plugin, module_file, pathname, description)

            logger.debug('User plugin %s loaded successfully' % plugin)

        finally:
            if module_file is not None:
                module_file.close()

    return plugin_module


def get_logger(name, config, logger=None):
    '''
    Returns a logger instance

    name      str (logging.Logger name)
    Config    dict with proper 'log-level' and 'log-destination' information

    Pass a logger to log about logging logs (woooa)
    '''
    log_level = config['log-level']
    log_types = config['log-destination'].split(',')

    if get_logging_level(log_level) is None:
        if logger is not None:
            logger.error('Logging level %s is invalid for plugin %s' % (log_level, name))
        else:
            print 'Logging level %s is invalid for plugin %s' % (log_level, name)
            return None

    newlogger = logging.getLogger(name)
    newlogger.propagate = False
    newlogger.setLevel(get_logging_level(log_level))

    for logtype in log_types:
        full_logtype = logtype.lower().strip()
        logtype = full_logtype.split(':')[0]

        if get_logging_type(logtype) is None:
            if logger is not None:
                logger.error('Logging destination %s is invalid for plugin %s' % (logtype, name))
            else:
                    print 'Logging destination %s is invalid for plugin %s' % (logtype, name)
                    continue

        if logtype == 'null':
            newlogger.addHandler(logging.NullHandler())

        elif logtype == 'file':
            try:
                FileHandler = logging.FileHandler(full_logtype.split(':')[1])
                FileHandler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s'))
                newlogger.addHandler(FileHandler)
            except:
                if logger is not None:
                    logger.error('Logging destination %s is invalid for plugin %s' % (full_logtype, name))
                else:
                        print 'Logging destination %s is invalid for plugin %s' % (full_logtype, name)
                        continue

        elif logtype == 'console':
            if get_logging_level(log_level) is logging.DEBUG:
                fmt = '%(name)s - %(levelname)s - %(message)s'
            elif get_logging_level(log_level) is logging.INFO:
                fmt = '%(name)s - %(message)s'
            else:
                fmt = '%(message)s'

            ConsoleHandler = logging.StreamHandler(sys.stdout)
            ConsoleHandler.setFormatter(logging.Formatter(fmt))
            newlogger.addHandler(ConsoleHandler)

        elif logtype == 'syslog':
            if len(full_logtype.split(':')) > 1:
                newlogger.addHandler(logging.handlers.SysLogHandler())
            elif len(full_logtype.split(':')) is 2:
                strfacility = full_logtype.split(':')[1]

                ip = ('localhost', logging.handlers.SYSLOG_UDP_PORT)

                if '@' in strfacility:
                    strfacility, ip[0] = strfacility.split('@')

                facility = get_syslog_facility(strfacility)

                if facility is not None:
                    facility = logging.handlers.SysLogHandler.LOG_USER

                try:
                    logger.addHandler(logging.handlers.SysLogHandler(address=ip, facility=facility))

                except:
                    if logger is not None:
                        logger.error('Logging syslog destination %s is invalid for plugin %s' % (full_logtype, name))
                    else:
                            print 'Logging syslog destination %s is invalid for plugin %s' % (full_logtype, name)
                            continue

        if logger is not None:
            logger.debug('Logger(s) initialized for %s' % name)

    return newlogger


def ansi_color_stripper(rawtext):
    '''
    Ref: http://stackoverflow.com/questions/2186919/getting-correct-string-length-in-python-for-strings-with-ansi-color-codes
    '''
    from pyparsing import Literal, Word, Combine, Optional, oneOf, Suppress, delimitedList, alphas, nums

    ESC = Literal('\x1b')
    integer = Word(nums)
    escapeSeq = Combine(ESC + '[' + Optional(delimitedList(integer, ';')) + oneOf(list(alphas)))

    nonAnsiString = lambda rawtext: Suppress(escapeSeq).transformString(rawtext)

    unColorString = nonAnsiString(rawtext)
    return unColorString
