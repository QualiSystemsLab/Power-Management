from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext
from PowerLib.Events import *
# from PowerLib.ShellDebugHelper import *


class PowerService (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    def AfterResourcesChanged(self, context, actionDetails, resourcesDetails, serviceDetails,
                              resourcesRemoved, resourcesAdded, modifiedResources):
        """
        Intervene after a resource is added, removed, or has an attribute changed
        :param ResourceCommandContext context: the context the command runs on
        :param str actionDetails: details about the action
        :param str resourcesDetails: details about the resource
        :param str serviceDetails: details about the service
        :param str resourcesRemoved: details about the added resources
        :param str resourcesAdded: details about the removed resources
        :param str modifiedResources: details about the modified resources
        """

        return after_resources_changed(context, resourcesAdded)

    # TODO Move to Async call and use 'Allow Unreserved' tag for Shutdown and Power off commands
    def BeforeResourcesChanged_Sync(self, context, actionDetails, resourcesDetails, serviceDetails, resourcesRemoved,
                                    resourcesAdded, resourcesModified):
        """
        Intervene before a resource is added, removed, or has an attribute changed
        :param ResourceCommandContext context: the context the command runs on
        :param str actionDetails: details about the action
        :param str resourcesDetails: details about the resource
        :param str serviceDetails: details about the service
        :param str resourcesRemoved: details about the added resources
        :param str resourcesAdded: details about the removed resources
        :param str resourcesModified: details about the modified resources
        """

        return before_resources_changed(context, resourcesRemoved)

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass


if __name__ == "__main__":
    # show_recording(PowerService)
    # playback(PowerService)
    pass
