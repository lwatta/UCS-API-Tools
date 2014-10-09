UCS-API-Tools
=============

Tools for querying or setting data in Cisco UCSM via python SDK

Most tools written for Nimbus specific requests like checking UCS settings before changes

UCSM_check_sp_template.py

	Used to make sure that Nova and Net node SPs are linked to a Template, 
	that the template is an updating template, and that the maintence policy 
	is set to USER_ACK.

	Simply takes a UCSM hostname or ip and password then searches thourgh SPs 
	looking for nova or net in the SP name.

ucsm_get_adpater_policy_settings.py

	Used to check the settings for TX/RX offload, queue size and ring size for specific settings we want
