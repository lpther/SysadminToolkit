"""
Wikipedia definition:
0    Emergency      System is unusable.

    A "panic" condition usually affecting multiple apps/servers/sites.
    At this level it would usually notify all tech staff on call.

1    Alert          Action must be taken immediately.

    Should be corrected immediately, therefore notify staff who can fix
    the problem. An example would be the loss of a primary ISP connection.

2    Critical       Critical conditions.

    Should be corrected immediately, but indicates failure in a primary
    system, an example is a loss of a backup ISP connection.

3    Error          Error conditions.

    Non-urgent failures, these should be relayed to developers or admins;
    each item must be resolved within a given time.

4    Warning        Warning conditions.

    Warning messages, not an error, but indication that an error will occur
    if action is not taken, e.g. file system 85% full - each item must be
    resolved within a given time.

5    Notice         Normal but significant condition.

    Events that are unusual but not error conditions - might be summarized
    in an email to developers or admins to spot potential problems - no
    immediate action required.

6    Informational  Informational messages.

    Normal operational messages - may be harvested for reporting, measuring
    throughput, etc. - no action required.

7    Debug          Debug-level messages.

    Info useful to developers for debugging the application, not useful
    during operations.
"""

loglevels = ['EMERGENCY', 'ALERT', 'CRITICAL', 'ERROR', 'WARNING', 'NOTICE', 'INFORMATIONAL', 'DEBUG']

from sysadmintoolkit import exception


class NullLogger(object):
    '''
    '''
    def __init__(self, loglevel):
        '''
        '''
        if isinstance(loglevel, int) and loglevel in range(8):
            self.loglevel = loglevel
        elif isinstance(loglevel, str) and loglevel.upper() in loglevels:
            self.loglevel = loglevels.index(loglevel.upper())
        else:
            raise exception.CommandPromptError('Cannot create logger instance, loglevel is invalid')

        self.loglevel = loglevel

    def log_emergency(self, msg):
        if self.loglevel >= 0:
            self.log_msg(msg)

    def log_alert(self, msg):
        if self.loglevel >= 1:
            self.log_msg(msg)

    def log_critical(self, msg):
        if self.loglevel >= 2:
            self.log_msg(msg)

    def log_error(self, msg):
        if self.loglevel >= 3:
            self.log_msg(msg)

    def log_warning(self, msg):
        if self.loglevel >= 4:
            self.log_msg(msg)

    def log_notice(self, msg):
        if self.loglevel >= 5:
            self.log_msg(msg)

    def log_info(self, msg):
        if self.loglevel >= 6:
            self.log_msg(msg)

    def log_debug(self, msg):
        if self.loglevel >= 7:
            self.log_msg(msg)

    def log_msg(self, msg, loglevel=None):
        pass


class StdoutLogger(NullLogger):
    def __init__(self, loglevel):
        NullLogger.__init__(self, loglevel)

    def log_msg(self, msg, loglevel=None):
        print msg
