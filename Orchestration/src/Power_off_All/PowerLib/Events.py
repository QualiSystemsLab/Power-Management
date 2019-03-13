from cloudshell.shell.core.driver_context import ResourceCommandContext
from Resources import ResourcesDetails
from Core import PowerLib


def after_resources_changed(context, added_resources):
    """
    Powers on the added resources

    :param ResourceCommandContext context: the context the command runs on
    :param str added_resources: details about the added resources
    """

    power = PowerLib.from_context(context)
    resources_details = ResourcesDetails(added_resources).resources

    if len(resources_details) == 0:
        power.logger.info("No Resources Added")
        return

    return power.power_on_resources(resources_details)


def before_resources_changed(context, removed_resources):
    """
    Powers off the removed resources

    :param ResourceCommandContext context: the context the command runs on
    :param str removed_resources: details about the removed resources
    """

    power = PowerLib.from_context(context)

    resources_details = ResourcesDetails(removed_resources).resources

    if len(resources_details) == 0:
        power.logger.debug("No Resourced Removed")
        return

    return power.power_off_resources(resources_details)
