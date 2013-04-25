import os
import textwrap
import sys
import tty
import termios
import fcntl
import struct


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


def get_reversed_text(text):
    return '\033[7m' + text + '\033[0m'


def get_bold_text(text):
    return '\033[1m' + text + '\033[0m'


def get_underline_text(text):
    return '\033[4m' + text + '\033[0m'


def get_dark_text(text):
    return '\033[2m' + text + '\033[0m'


def print_config_contents(config):
    print 'External and default configuration loaded'
    print
    width = min(get_terminal_size()[0], 100)

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


def pager(text, height):
    ''''
    print lines to screen and mimic behaviour of MORE command

    # Code from: http://code.activestate.com/recipes/134892/ and
    # https://raw.github.com/khosrow/lvsm/master/lvsm/utils.py
    '''
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    more = ' ' + get_reversed_text('-- More -- ')

    i = 0
    if text is not None:
        for line in text.splitlines():
            i = i + 1
            if height and i is int(height):
                print more + "\r",
                ch = getch()
                # erase the "-- More --"
                print "             \r",
                # pressing 'q' will go back to prompt
                # pressing 'enter' will advance by 1 line
                # otherwise show next page
                if ord(ch) == 113:
                    return
                elif ord(ch) == 13:
                    i = i - 1
                else:
                    i = 0
            print line.rstrip()
