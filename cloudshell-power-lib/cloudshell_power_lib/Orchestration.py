from Core import PowerLib
from cloudshell.api.cloudshell_api import ReservedResourceInfo
from Resources import ResourcesDetails
from cloudshell.workflow.orchestration.sandbox import Sandbox


def power_on_resources_in_sandbox(sandbox, resources=None):
    """
    Attempts power-on for the specified resources in the sandbox.
    If resources is None, will attempt power-on for all resources in the sandbox

    :param Sandbox sandbox: Sandbox object to operate on
    :param dict[ReservedResourceInfo] resources: resources to power on
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

    :param Sandbox sandbox: Sandbox object to operate on
    :param dict[ReservedResourceInfo] resources: resources to power off
    :return:
    """
    power = PowerLib.from_sandbox(sandbox)

    if resources is None:
        resources = sandbox.components.resources
    resources_details = ResourcesDetails.create_from_ReservedResourceInfo_dict(resources)

    return power.power_off_resources(resources_details)


def add_power_service_to_sandbox(sandbox, service_name=None):
        """

        :param Sandbox sandbox: Sandbox object to operate on
        :param str service_name: Name of the service to add
        :return:
        """
        if service_name is None:
            service_name = 'Power'

        power = PowerLib.from_sandbox(sandbox)

        existing_service_check = \
            [x.ResourceName for x in power.api_session.GetReservationServicesPositions(reservationId=power.reservation_id).ResourceDiagramLayouts if x.ResourceName == service_name]

        if len(existing_service_check) == 0:
            power.logger.info("Adding Service {} to reservation".format(service_name))
            power.api_session.AddServiceToReservation(reservationId=power.reservation_id, serviceName=service_name,  alias=service_name)
        else:
            power.logger.warn("Service '{}' already in reservation".format(service_name))
