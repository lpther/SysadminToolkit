
# SysadminToolkit

Easily create CLIs from your many and specialized scripts and tools, or code your python based plugins for advanced tasks.

## Target Audience ##

If you are a System Administrator (server, network, storage, database, application, or any other field of expertise), and must support a somewhat large infrastructure, chances are that every group have their own set of tools with no real coding standards.

Even worse, you might need the other team's tools to troubleshoot systems you support, and a minuscule typo in one of their scripts could lead to a disaster, without talking about the complexity of maintaining centralized documentation up to date (if you even have access to their documentation that is!).

With this package, you hide the complexity of your tools (or just a subset of useful commands), describe what that does, and easily maintain this *indirection*. 

The real end user of what you put into your toolkit might not even be you, as most of your tasks are complex and the added burden of a CLI is not worth it, but Admins from other teams could do the basic troubleshooting before requiring your actual intervention.

If you are a python coder, even a beginner, you could code your own plugin to use the CLI's features, provide commands that operators can run, log to a centralized logging server, etc.

## Installation ##

SysadminToolkit is coded for python 2.7 (conversion to 3.x will follow) on Ubuntu 12.04, and requires the following packages:

- Pyparsing ([http://pyparsing.wikispaces.com/](http://pyparsing.wikispaces.com/))

*Installation details to follow*

## Basic Usage ##

With a simple configuration file, you can map CLI commands to a shell command or an external script, and provide a short help of what your command does:

    [shellcommand]
    cmd-display_system_uptime = date \; uptime
    help-display_system_uptime = Shows the current time, number of users and load


Launching the app will let you use the configured command to hide more complex tasks, and display a list of all available commands and their help:

    user@somemachine:~/$ sysadmin-toolkit

    sysadmin-toolkit# display system uptime
     22:40:36 up 3 days,  5:54, 21 users,  load average: 0.20, 0.09, 0.15
    Fri May  3 22:40:36 GMT 2013

    sysadmin-toolkit# debug commandprompt
      Loaded plugins: commandprompt, shellcommand
    
      Command tree (operator)
      =======================

        Definitions: non executable, executable, <dynamic>

      Keyword                                    Help (plugin)
    ------------------------------------------------------------------------------
    debug                                        Debug plugins (commandprompt)

    debug commandprompt                          Displays registered commands in the
                                                 current Command Prompt
                                                 (commandprompt)

    display system uptime                        Shows the current number of users
                                                 and load (shellcommand)
    [...]

## Features ##

Initial release (0.1.0) features:

- CLI Features
	- Call a command from linux's shell
	- Command completion (bash style) **not yet functionnal**
	- Command conflict handling for cases where a label is entered by multiple plugins
	- "|" support to redirect a command to another process **not yet functionnal**
	- "?" shows contextual help **not yet functionnal**
	- Plugins can use dynamic keywords, with full autocompletion and conflict handling support
	- Mode based CLI can be created: operator, root or configuration. Each mode could have a different set of commands. **not yet functionnal**
	- All help is based on python docstrings, to ease documentation for your commands
- Built-in plugins
	- commandprompt - for debugging and most built-in commands
	- shellcommand - simple label to shell mapping/help
- Flexible configuration
	- Any configuration block is passed to plugins
	- Logging can be customized per plugin or globally:
		- File
		- Console
		- SysLog (remote or local)

## Related projects ##

Code plugins that leverage the toolkit for advanced features (why this project started in the first place)

- clustering - basic cluster management features
- lvs/keepalived - linux virtual server and keepalived for an any-node load balancing cluster
- fibre channel - fibre channel troubleshooting toolkit
- infiniband - infiniband troubleshooting toolkit
	
## Thanks ##

Khosrow Ebrahimpour for his invaluable talent and charisma

