# Future features and nice to haves #

Brainstorming about potential improvements

## Code ##

- Convert to python 3.x compatible code
- Code documentation
- Add more unit testing
    - Badly behaving dynamic keyword fn
    - Prefix conflict with dynamic keyord

## Functionality ##

- Contextual help via '?'
- External command call via '!'
- ctrl-C to quit the program (requires flushing readline's buffer and quitting)
- 'enable-plugin=no' in the config to prevent from loading a module without erasing the configuration

## CommandPrompt (built-in plugin) ##

- Scoping to resolve command conflicts, via the 'use' command
- Multiple mode support: operator -> root, root -> config
- Clear plugin cache to broadcast a message to all plugins to clear their caches

## ShellCommand (built-in plugin) ##

- Provide the 'debug shellcommand' command to list registered labels and shorthelp