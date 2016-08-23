Standalone scripts to run against a standalone C-series servers
	aka no UCSM FI

API_yaml based script
	- single script that takes a yaml file in as input to be 
	executed against a single UCS CIMC controller
	- benefit is that you simple modify or create a new yaml
	over creating a new script. Very powerful. Can be stuck 
	into ansible to run against many hosts at the same time.
	Takes about 15 minutes to configure 32 servers.
