import os
import textwrap
import sys
import termios
import fcntl
import struct
import logging


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

    except:

        try:
            hw = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            hw = (25, 80)

    return hw


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
    block    [(str,window%,maxwidth)]    Prints the str for a ratio of window size, without exceeding maxwidth
    '''
    window_width = get_terminal_size()[1]

    vertical_blocks = []
    vertical_blocks_len = []

    for block in blocks:
        (blockstr, window_ratio, maxwidth) = block

        width = min(int(window_width * window_ratio), int(maxwidth))

        vertical_blocks += [(textwrap.wrap(blockstr, width=width), width)]
        vertical_blocks_len += [len(textwrap.wrap(blockstr, width=width))]

    for index in range(max(vertical_blocks_len)):
        for vertical_block in vertical_blocks:
            (blockstr, width) = vertical_block

            if len(blockstr) > index:
                # Remove ansi color chars as they mess up string lengths
                uncolored_blockstr = ansi_color_stripper(blockstr[index])
                nb_ansi_color_chars = len(blockstr[index]) - len(uncolored_blockstr)

                print blockstr[index].ljust(width) + (' ' * nb_ansi_color_chars),
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


def print_config_contents(config):
    print 'External and default configuration loaded'
    print
    width = min(get_terminal_size()[1], 100)

    sections = config.sections()
    sections.sort()

    for section in sections:
        print '  Section %s' % section
        print
        print '    %s %s' % ('Option'.ljust(int(width * 0.5)), 'Value')
        print '    %s %s' % ('------'.ljust(int(width * 0.5)), '-----')

        options = config.options(section)
        options.sort()

        for option in options:
            value = config.get(section, option)
            print '    %s %s' % (option.ljust(int(width * 0.5)), value)

        print


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


def set_config_logging(config, log_destination, log_level):
    '''
    for each config section, set log-destination and log-level to
    the appropriate values.

    None will make no changes

    '''
    for section in config.sections():
        if log_destination is not None:
            config.set(section, 'log-destination', log_destination)

        if log_level is not None:
            config.set(section, 'log-level', log_level)


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


def get_logger(name, config, logger=None):
    '''
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
                newlogger.addHandler(logging.FileHandler(full_logtype.split(':')[1]))
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

                facility = get_syslog_facility(strfacility)
                if facility is not None:
                    logger.newaddHandler(logging.handlers.SysLogHandler(facility=facility))
                else:
                    if logger is not None:
                        logger.error('Logging syslog destination %s is invalid for plugin %s (bad facility)' % (full_logtype, name))
                    else:
                            print 'Logging syslog destination %s is invalid for plugin %s (bad facility)' % (full_logtype, name)
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
