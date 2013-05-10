# Plugin Design Guide #

## Terminology ##

- Label: This is a command typed by a user in the CLI. Ex: 'display system uptime'
- Keyword: A single word in a command. Ex: In the previous example, 'uptime' is a keyword

## Command Prompt interaction with plugins ##

Everything starts with the __ main__.py's excution, which connects all the parts: plugins, command prompt and configuration.

1. Parsing of arguments passed by the calling shell.
2. Reading of the configuration file (default is /etc/sysadmin-toolkit/sysadmin-toolkit.conf, but can be overridden by the arguments.
3. Defaults configuration is populated into the configuration file.
4. Plugins listed in the configuration file are loaded, and each plugin's get_plugin() is called to retrieve the instance. 
	1.  Each plugin is called with their own logger instance and configuration block.
	2.  Basic plugin initialization should be made here, all commands that do not depend on other modules should be registered here.
5. If the calling user is root, the commandprompt is instantiated in root mode, any other user will cause the commandprompt to be instantiated in operator mode. Note that the mode is only meaningful to plugins, as the registered commands might be different depending on the mode.
6. Each loaded plugin is updated with the list of all available plugins. This makes each plugin aware of other plugins, so inter-plugin calls can be made easily.
7. Each plugin is added to the initial commandprompt. This causes the following reaction:
	1. For each plugin added, the commandprompt registers both commands associated to the current mode (root or  operator initially), **AND** commands defined in the default mode.
	2. The process of registering consists in inserting it in a tree structure, with each level of the tree a 'keyword' with it's attribute, and a list of sub-keywords.
	3. Keywords are added to the tree regardless of conflicts. The only conflict that is prohibited is a reserved command vs a non-reserved command. Only the built-in plugin CommandPrompt inserts reserved commands.
8. The commandprompt then enters the loop mode, where it loops over user input to dispatch commands to plugins. If the calling shell passed commands, these commands are executed in sequence then the program terminates.
	1. Entering the loop mode calls the each plugin's enter_mode() hook method. This adds the calling commandprompt to the plugin's cmdstack.
	2. Leaving the loop mode (by a user quitting) will call the leave_mode() hook method. This removes the last commandprompt from the plugin's cmdstack.

## Designing a plugin ##

*To be continued*