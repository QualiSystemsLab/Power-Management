from PowerLib.Orchestration import power_on_resources_in_sandbox
from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.workflow.orchestration.setup.default_setup_orchestrator import DefaultSetupWorkflow
import cloudshell.helpers.scripts.cloudshell_dev_helpers as dev_helpers


dev_helpers.attach_to_cloudshell()

sandbox = Sandbox()

DefaultSetupWorkflow().register(sandbox)

# Uncomment if you want to automatically add the power service to the reservation
# sandbox.workflow.add_to_preparation(PowerLib.add_power_service_to_reservation, 'Power')

sandbox.workflow.add_to_provisioning(power_on_resources_in_sandbox, components=None)


sandbox.execute_setup()
