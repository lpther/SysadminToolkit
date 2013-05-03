=====================================================================================
SysadminToolkit - Easily create CLIs from your many and specialized scripts and tools
=====================================================================================

Terminology:
	label		: full command, ex: "display system uptime"
	keyword		: a word from a label, separated from a <space>. Must not 
				  contain a special character (see below)
	
Reserved labels:
	"mod ..."				: restrict the scope of the following label to one plugin (later)
	"help <pluginname>"		: display the plugin's main help (later)
	"exit ..."				: exits current mode, go back to previous mode if available (later)
	"quit ..."				: exits to shell (later)
	"set ..."				: change configuration during run time (later)
	
Special character meanings:
	" " (space)		: keyword separator
	?				: contextual help (later)
	<keyword>		: dynamic keyword
	\n				: execute current label
	tab				: command completion (later)
	
	Note: All other characters can be used by modules
  
* Features

Current features:
	Broken
	
Initial release features:
	CLI Features
	[x]	Call from linux's shell
	[x]	Functional plugins mechanics
	
	Built-in plugins
	[x]	commandprompt (debugging)
	[x]	shellcommand  (simple label to shell mapping/help)
		
	Installation and configuration
	[x]	Basic configuration file loading, passing the config to plugins
	[x]	Configurable logging 
	
Soon after:
	Documentation
		Describe the target audience
		
	CLI Features
	[x]	Command completion
		Contextual help
		Notify plugins to clear cache when changing modes
	[x]	Dynamic keyword support
		
	Installation and configuration
		Make setup.py works for install
	
Later:
	Convert to nice md or rst text
	Support parsing of main config file
	[x]	Parsing and loading default
	[x]	Plugin definition here
[x]	Support for same label, but different plugin (conflict handling)
	Sudo-like use, ex: operator account could switch to root for the scope of the CLI or the submode
[x]	Advanced logging (syslog/remote syslog)
	Plugin design philosophy
	Design document and expand documentation
	Maximize docstring usage in plugins, for easy documentation for the sysadmins ;-)
	Documentation for sysadmins for easily package toolkit with their tools

Out of scope:
	Code plugins that leverage the toolkit for advanced features (why this project started in the first place)
		clustering (symmetric and group based)
		lvs/keepalived
		fibre channel toolkit
		infiniband toolkit
	
* Requires
	pyparsing
	
* Thanks

Khosrow Ebrahimpour for his invaluable talent and charisma
Wikipedia
