"""
This is a test script to validate that the enqueue resource command is valid.
It is designed to be attached to the device and call a command it contains
"""

import cloudshell.helpers.scripts.cloudshell_scripts_helpers as cs_helper
import cloudshell.helpers.scripts.cloudshell_dev_helpers as dev_help

# ======================================
# debug global vars - used with dev_help
_d_resid = '77502c5b-e089-46b1-b363-149cbfa44402'
_d_user = 'admin'
_d_pwrd = 'admin'
_d_domain = 'Global'
_d_server = 'localhost'
_d_api_port = '8029'
_d_resource = 'AUS_2'

dev_help.attach_to_cloudshell_as(_d_user, _d_pwrd, _d_domain, _d_resid,
                                 server_address=_d_server, cloudshell_api_port=_d_api_port, command_parameters={},
                                 resource_name=_d_resource)
# End DeBug section
# ======================================


def _item_in_list(i, l):
    try:
        idx = l.index(i)
        return True
    except:
        return False


# white_list = ['power_on', 'power on', 'Power On']
white_list = ["Graceful Shutdown", "shutdown", "graceful_shutdown"]
# white_list = ["power_off", "Power Off", "Power OFF"]
who_am_i = cs_helper.get_resource_context_details().fullname

res_id = cs_helper.get_reservation_context_details().id

cmd_list = []
cmds = cs_helper.get_api_session().GetResourceCommands(who_am_i).Commands

for each in cmds:
    cmd_list.append(each.Name)
my_cmd = 'No Command'
cmd_check = False
for cmd_name in cmd_list:
    if _item_in_list(cmd_name, white_list):
        my_cmd = cmd_name
        cmd_check = True
        break

print my_cmd

if cmd_check:
    full_detail = cs_helper.get_api_session().GetResourceDetails(who_am_i)
    cs_helper.get_api_session().WriteMessageToReservationOutput(res_id, '\n>>>> Calling Command <<<<\n\n')
    # cs_helper.get_api_session().EnqueueResourceCommand(res_id, who_am_i, my_cmd)
    # cs_helper.get_api_session().ExecuteResourceCommand(res_id, resourceFullPath=who_am_i, commandName=my_cmd)
    # cs_helper.get_api_session().ExecuteCommand(res_id,who_am_i,'Resource',my_cmd)
    cs_helper.get_api_session().EnqueueCommand(res_id, who_am_i, 'Resource', my_cmd)

