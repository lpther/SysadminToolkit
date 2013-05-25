# Future features and nice to haves #

Brainstorming about potential improvements

## Code ##

- Convert to python 3.x compatible code
- Code documentation
- Add more unit testing
    - Badly behaving dynamic keyword fn
    - Prefix conflict with dynamic keyword
    - Multiple modes support

## Functionality ##

- Contextual help via '?'
- External command call via '!'
- ctrl-C to quit the program, requires flushing readline's buffer and quitting (dragons ahead)
- 'enable-plugin=no' in the config to prevent from loading a module without erasing the configuration
- Make a master debug log, separate from other logging config, where all debug level logs would be merged to a file

## CommandPrompt (built-in plugin) ##

- Scoping to resolve command conflicts, via the 'use' command (dragons ahead)
- Multiple mode support: operator -> root, root -> config
- Clear plugin cache to broadcast a message to all plugins to clear their caches

## ShellCommand (built-in plugin) ##

- Provide the 'debug shellcommand' command to list registered labels and shorthelp