===============
SysadminToolkit
===============

Terminology:
	label		: full command, ex: "display system time"
	keyword		: a word from a label, separated from a <space>. Must not 
				  contain a special character (see below)
	
Reserved labels:
	"mod ..."			: restrict the scope of the following label to one plugin
	"help <pluginname>"	: display the plugin's main help
	"exit ..."			: exits current mode, go back to previous mode if available
	"quit ..."			: exits to shell
	"set ..."			: change configuration during run time
	
Special character meanings:
	" " (space)	: keyword separator
	?			: contextual help
	</>			: dynamic keyword
	\n			: execute current label
	tab			: command completion
	
	Note: All other characters can be used by modules
  
* Features

Current features:
	Broken
	
Initial release features:
	Functionnal plugins
	Call from linux's shell
	
Soon after:
	Command completion
	Contextual help
	Notify plugins to clear cache when changing modes
	
Later:
	Support parsing of main config file
	Sudo-like use, ex: operator account could switch to root for the scope of the CLI or the submode
	Advanced logging (syslog/remote syslog)
	
* Thanks

Khosrow Ebrahimpour for is invaluable talent and charisma
Wikipedia