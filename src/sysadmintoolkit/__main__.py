from sysadmintoolkit import cmdprompt, logger, builtinpkg
from builtinpkg import commandprompt

if __name__ == '__main__':
    stdoutlogger = logger.StdoutLogger(7)

    stdoutlogger.log_debug("Started sysadmintoolkit __main__.py")

    rootcmdprompt = cmdprompt.CmdPrompt(stdoutlogger)

    rootcmdprompt.cmdloop()
