from cloudshell_power_lib.Orchestration import power_off_resources_in_sandbox
from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.workflow.orchestration.teardown.default_teardown_orchestrator import DefaultTeardownWorkflow
import cloudshell.helpers.scripts.cloudshell_dev_helpers as dev_helpers


dev_helpers.attach_to_cloudshell()

sandbox = Sandbox()

DefaultTeardownWorkflow().register(sandbox)

sandbox.workflow.add_to_teardown(power_off_resources_in_sandbox, components=None)

sandbox.execute_teardown()
