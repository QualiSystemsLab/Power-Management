from PowerLib import PowerLib
from cloudshell.api.cloudshell_api import ReservedResourceInfo
from input_converters import ResourcesDetails
from cloudshell.workflow.orchestration.sandbox import Sandbox


def power_on_resources_in_sandbox(sandbox, resources=None):
    """
    Attempts power-on for the specified resources in the sandbox.
    If resources is None, will attempt power-on for all resources in the sandbox

    :param Sandbox sandbox:
    :param dict[ReservedResourceInfo] resources:
    :return:
    """
    power = PowerLib.from_sandbox(sandbox)

    if resources is None:
        resources = sandbox.components.resources
    resources_details = ResourcesDetails.create_from_ReservedResourceInfo_dict(resources)

    return power.power_on_resources(resources_details)


def power_off_resources_in_sandbox(sandbox, resources=None):
    """
    Attempts power-off for the specified resources in the sandbox.
    If resources is None, will attempt power-off for all resources in the sandbox

    :param Sandbox sandbox:
    :param dict[ReservedResourceInfo] resources:
    :return:
    """
    power = PowerLib.from_sandbox(sandbox)

    if resources is None:
        resources = sandbox.components.resources
    resources_details = ResourcesDetails.create_from_ReservedResourceInfo_dict(resources)

    return power.power_off_resources(resources_details)
