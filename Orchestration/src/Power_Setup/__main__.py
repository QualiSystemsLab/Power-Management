from cloudshell_power_lib.Orchestration import power_on_resources_in_sandbox
from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.workflow.orchestration.setup.default_setup_orchestrator import DefaultSetupWorkflow
import cloudshell.helpers.scripts.cloudshell_dev_helpers as dev_helpers
# Uncomment to add power service to reservation automatically (1 of 2)
# from cloudshell_power_lib.Orchestration import add_power_service_to_sandbox

dev_helpers.attach_to_cloudshell()

sandbox = Sandbox()

DefaultSetupWorkflow().register(sandbox)

# Uncomment to add power service to reservation automatically (2 of 2)
# sandbox.workflow.add_to_preparation(add_power_service_to_sandbox, 'Power')

sandbox.workflow.add_to_provisioning(power_on_resources_in_sandbox, components=None)


sandbox.execute_setup()
