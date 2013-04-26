=====================================================================================
SysadminToolkit - Easily create CLIs from your many and specialized scripts and tools
=====================================================================================

Terminology:
	label		: full command, ex: "display system time"
	keyword		: a word from a label, separated from a <space>. Must not 
				  contain a special character (see below)
	
Reserved labels:
	"mod ..."				: restrict the scope of the following label to one plugin
	"help <pluginname>"		: display the plugin's main help
	"exit ..."				: exits current mode, go back to previous mode if available
	"quit ..."				: exits to shell
	"set ..."				: change configuration during run time
	
Special character meanings:
	" " (space)		: keyword separator
	?				: contextual help
	<keyword>		: dynamic keyword
	\n				: execute current label
	tab				: command completion
	
	Note: All other characters can be used by modules
  
* Features

Current features:
	Broken
	
Initial release features:
	CLI Features
	[x]	Call from linux's shell
		Functional plugins mechanics
	
	Built-in plugins
		commandprompt (debugging)
		shellcommand  (simple label to shell mapping/help)
		
	Installation and configuration
		Basic configuration file loading, passing the config to plugins
		Configurable logging 
	
Soon after:
	Documentation
		Describe the target audience
		Dynamic keyword support
		
	CLI Features
		Command completion
		Contextual help
		Notify plugins to clear cache when changing modes
		
	Installation and configuration
		Make setup.py works for install
	
Later:
	Convert to nice md or rst text
	Support parsing of main config file
		Parse and type checking
		Plugin definition here
	Support for simple label to shell command mapping
	Support for same label, but different plugin (conflict handling)
	Sudo-like use, ex: operator account could switch to root for the scope of the CLI or the submode
	Advanced logging (syslog/remote syslog)
	Plugin design philosophy
	Design document and expand documentation
	Maximize docstring usage in plugins, for easy documentation for the sysadmins ;-)
	Documentation for sysadmins for easily package toolkit with their tools

Out of scope:
	Code plugins that leverage the toolkit for advanced features (why this project started in the first place)
		clustering (symmetric and group based)
		lvs/keepalive
		fibre channel toolkit
		infiniband toolkit
	
* Thanks

Khosrow Ebrahimpour for is invaluable talent and charisma
Wikipedia
