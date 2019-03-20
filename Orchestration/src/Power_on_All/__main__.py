from cloudshell_power_lib.Orchestration import power_on_resources_in_sandbox
from cloudshell.workflow.orchestration.sandbox import Sandbox
import cloudshell.helpers.scripts.cloudshell_dev_helpers as dev_helpers


dev_helpers.attach_to_cloudshell()

sandbox = Sandbox()

power_on_resources_in_sandbox(sandbox)
