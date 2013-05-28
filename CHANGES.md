# Changes #

## SysadminToolkit ##

**0.1.0b - May 25 2013**

- Minor bug fixes
- Output refining for plugin errors (tracebacks) 
- "-n" disables name resolution for all plugins (if implemented by plugins)

**0.1.0a - May 10 2013**

- Initial release
- Auto completion
- Dynamic keywords
- '|' support to redirect a command's output
- Callable from Linux's shell with a command
- Single mode command prompt (root or operator depending on the user)
- stdout, syslog or file logging
- Configuration file support
	- Configuration file parsing
	- Per plugin configuration block
- Plugin support
	- Functional plugin mechanics
	- Plugin loading and basic programming error output

## CommandPrompt (built-in plugin) ##

**HEAD revision**

- Help command can now convert to reStructuredText to fancy documentation format

**0.1.0b - May 25**

- Help command to access plugin's docstrings
- Switchmode command can switch between "root" and "config" modes, to have minimal command sorting
- Plugin's documentation is available directly in the code

**0.1.0a - May 10 2013**

- Initial release
- 'debug commandprompt' displays a list of all registered commands and shorthelp

## ShellCommand (built-in plugin) ##

**0.1.0b - May 25**

- Plugin's documentation is available directly in the code

**0.1.0a - May 10 2013**

- Initial release
- Label and shorthelp to label mapping