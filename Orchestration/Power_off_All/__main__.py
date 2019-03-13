from PowerLib.Orchestration import power_off_resources_in_sandbox
from cloudshell.workflow.orchestration.sandbox import Sandbox
import cloudshell.helpers.scripts.cloudshell_dev_helpers as dev_helpers


dev_helpers.attach_to_cloudshell()

sandbox = Sandbox()

power_off_resources_in_sandbox(sandbox)
