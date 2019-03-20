from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from ScreenLogger import *
from cloudshell.shell.core.driver_context import ResourceCommandContext
from Resources import ResourceDetails
from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.api.cloudshell_api import CloudShellAPISession
import cloudshell.api.cloudshell_api as cs_api


class PowerLib(object):
    def __init__(self):
        self.logger = None

        self.api_session = None  # type: CloudShellAPISession
        self.reservation_id = None

        # Command Lists
        self.power_on_command_names = ["power_on", "Power On", "Power ON",
                                       "PowerOn"]
        self.power_off_command_names = ["power_off", "Power Off", "Power OFF",
                                        "PowerOff"]
        self.shutdown_command_names = ["Graceful Shutdown", "shutdown",
                                       "graceful_shutdown", "Graceful_Shutdown"]

    @classmethod
    def from_sandbox(cls, sandbox):
        """

        :param Sandbox sandbox:
        :return:
        """
        self = cls()
        self.logger = add_screen_to_logger(sandbox.logger,
                                           sandbox.automation_api,
                                           sandbox.reservationContextDetails.id)
        self.api_session = sandbox.automation_api
        self.reservation_id = sandbox.reservationContextDetails.id
        return self

    @classmethod
    def from_context(cls, context):
        """

        :param ResourceCommandContext context:
        :return:
        """
        self = cls()
        self.logger = get_reservation_output_logger(context)

        self.api_session = cs_api.CloudShellAPISession(
            context.connectivity.server_address,
            domain=context.reservation.domain,
            token_id=context.connectivity.admin_auth_token)
        self.reservation_id = context.reservation.reservation_id
        return self

    def get_power_on_command(self, resource):
        """
        Returns Power On command

        :param ResourceDetails resource: The resource to power on
        :return:
        """
        command = [x.Name for x in
                   self.api_session.GetResourceConnectedCommands(resource.fullname).Commands
                   if x.Name in self.power_on_command_names]
        if len(command) == 0:
            return None
        elif len(command) == 1:
            return command[0]
        else:
            self.logger.warn("Multiple power-on commands found")
            return command[0]

    def power_on_resource(self, resource):
        """
        Attempts resource power on

        :param ResourceDetails resource: Resource to power on
        :return:
        :rtype
        """

        check = self.is_there_a_reason_to_not_power_on(resource)
        if check is not None:
            return check

        command = self.get_power_on_command(resource)
        if command is None:
            return "No Power-On Command"

        try:
            self.api_session.PowerOnResource(self.reservation_id,
                                             resource.fullname)
        except CloudShellAPIError as e:
            self.logger.error(e)
            return e.message
        return None

    def get_power_off_command(self, resource):
        """

        :param ResourceDetails resource:
        :return:
        """
        command = [x.Name for x in
                   self.api_session.GetResourceConnectedCommands(resource.fullname).Commands
                   if x.Name in self.power_off_command_names]
        if len(command) == 0:
            return None
        elif len(command) == 1:
            return command[0]
        else:
            self.logger.warn("Multiple power-off commands found")
            return command[0]

    def force_power_off_resource(self, resource):
        """
        Cuts power to the resource

        :param ResourceDetails resource: Resource to power-off
        :return:
        :rtype
        """

        check = self.is_there_a_reason_to_not_power_off(resource)
        if check is not None:
            return check

        command = self.get_power_off_command(resource)
        if command is None:
            return "No Power-Off Command"

        try:
            self.api_session.PowerOffResource(self.reservation_id,
                                              resource.fullname)
        except CloudShellAPIError as e:
            self.logger.error(e)
            return e.message
        return None

    def power_off_resource(self, resource):
        """
        Shuts down the resource if possible, else cuts power to the resource

        :param ResourceDetails resource: Resource to power-off
        :return:
        :rtype
        """

        check = self.is_there_a_reason_to_not_power_off(resource)
        if check is not None:
            return check

        if self.shutdown_resource(resource) is None:
            # Shutdown Succeeded
            return None
        # Shutdown Failed
        return self.force_power_off_resource(resource)

    def get_shutdown_command(self, resource):
        """

        :param ResourceDetails resource: The Resource
        :return: Shutdown Command or 'None'
        """
        command = [x.Name for x in
                   self.api_session.GetResourceCommands(resource.fullname).Commands
                   if x.Name in self.shutdown_command_names]
        if len(command) == 0:
            return None
        elif len(command) == 1:
            return command[0]
        else:
            self.logger.warn("Multiple shutdown commands found")
            return command[0]
        pass

    def shutdown_resource(self, resource):
        """
        Attempts to shutdown the resource gracefully
        :param ResourceDetails resource:
        :return:
        """

        check = self.is_there_a_reason_to_not_power_off(resource)
        if check is not None:
            return check

        command = self.get_shutdown_command(resource)
        if command is None:
            return "No Shutdown Command"

        try:
            self.api_session.ExecuteCommand(self.reservation_id,
                                            targetName=resource.fullname,
                                            targetType='Resource',
                                            commandName=command,
                                            printOutput=True)
        except CloudShellAPIError as e:
            self.logger.error(e)
            return e.message
        return None

    def _check_power_mgmt_flag(self, resource):
        """

        :param ResourceDetails resource:
        :return:
        """
        values = [x.Value for x in
                  self.api_session.GetResourceDetails(resource.fullname).ResourceAttributes
                  if x.Name.endswith(".Power Management")
                  or x.Name == "Power Management"]
        if len(values) == 0:
            return None
        elif len(values) == 1:
            return values[0]
        else:
            self.logger.warn("Multiple Power Management Flags found")
            return values[0]

    def is_there_a_reason_to_not_control_power(self, resource):
        """
        Returns a reason to not power control the resource (if applicable)
        Already included in both power-on and power-off check functions

        :param ResourceDetails resource: Resource to check
        :return: None or string specifying the reason
        :rtype str
        """
        if resource.subresource is True:
            return "No power-control for sub-resources"

        power_flag = self._check_power_mgmt_flag(resource)
        if power_flag is None:
            return "Power Management Attribute Not Found. Default to not controlling power"
        if power_flag is False:
            return "Power Management Attribute set to False"

        if resource.isShared is True:
            return "Can't power control shared resources"

        # No Reason
        return None

    def is_there_a_reason_to_not_power_on(self, resource):
        """
        Returns a reason to not power on the resource (if applicable)

        :param ResourceDetails resource: Resource to check
        :return: None or string specifying the reason
        :rtype str
        """
        # Perform General Checks
        general_result = self.is_there_a_reason_to_not_control_power(resource)
        if general_result is not None:
            return general_result

        # Check for Power On Command
        command = self.get_power_on_command(resource)
        if command is None:
            return "No power-on command available for resource"

        # No reason
        return None

    def is_there_a_reason_to_not_power_off(self, resource):
        """
        Returns a reason to not power off the resource (if applicable)

        :param ResourceDetails resource: Resource to check
        :return: None or string specifying the reason
        :rtype str
        """
        # Perform General Checks
        general_result = self.is_there_a_reason_to_not_control_power(resource)
        if general_result is not None:
            return general_result

        # Check for Power Off Command
        off_command = self.get_power_off_command(resource)
        shutdown_command = self.get_shutdown_command(resource)
        if off_command is None and shutdown_command is None:
            return "No power off or shutdown command available for resource"

        # Todo Add check for resource is in another reservation
        # Todo  -- Not needed since we don't work with shared resources???

        # No reason
        return None

    def power_on_reservation(self):
        """
        Attempts resource power on all resources in the reservation

        :return:
        :rtype
        """
        resources = [ResourceDetails.create_from_ReservedResourceInfo(x) for x
                     in self.api_session.GetReservationDetails(
                reservationId=self.reservation_id).ReservationDescription.Resources]
        self.power_on_resources(resources)

    def power_off_reservation(self):
        """
        Attempts to power off all resources in the reservation

        :return:
        :rtype
        """
        resources = [ResourceDetails.create_from_ReservedResourceInfo(x) for x
                     in self.api_session.GetReservationDetails(
                reservationId=self.reservation_id).ReservationDescription.Resources]
        self.power_off_resources(resources)

    def power_on_resources(self, resources):
        """

        :param list(ResourceDetails) resources:
        :return:
        """
        for resource in resources:  # type: ResourceDetails
            if resource.subresource is True:
                # Leave this uncommented
                self.logger.debug("Silently Skipping Sub-resource {}".format(resource.fullname))
                continue
            #     reason_to_skip = self.is_there_a_reason_to_not_power_off(resource)
            #     if reason_to_skip is not None:
            #         self.logger.log(SCREEN_INFO, "Not Powering Off {}: {}".format(resource.fullname, reason_to_skip))
            #         continue
            self.logger.log(SCREEN_INFO, "Attempting Power-on for {}".format(resource.fullname))
            error = self.power_on_resource(resource)
            if error is not None:
                self.logger.log(SCREEN_INFO, "Power-on Failed: for {}: {}".format(resource.fullname, error))

    def power_off_resources(self, resources):
        for resource in resources:
            if resource.subresource is True:
                self.logger.debug("Silently Skipping Sub-resource {}".format(resource.fullname))
                continue
            self.logger.log(SCREEN_INFO, "Attempting Power-off for {}".format(resource.fullname))
            error = self.power_off_resource(resource)
            if error is not None:
                self.logger.log(SCREEN_INFO, "Power-off Failed: for {}: {}".format(resource.fullname, error))

