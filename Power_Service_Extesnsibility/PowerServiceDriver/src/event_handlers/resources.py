import sys
from input_converters import *
from cloudshell.shell.core.driver_context import ResourceCommandContext
from cloudshell.core.logger.qs_logger import get_qs_logger

SEVERITY_INFO = 20
SEVERITY_ERROR = 40


class QualiError(Exception):
    def __init__(self, name, message):
        self.message = message
        self.name = name

    def __str__(self):
        return 'CloudShell error at ' + self.name + '. Error is:' + self.message


class ResourcesEvents:
    def __init__(self, api_session, reservation_id):
        self.logger = get_qs_logger("extensibility", "QS", "service")
        self.api_session = api_session
        self.id = reservation_id
        self.power_on_wl = ["power_on", "Power On", "Power ON"]  # whitelist for power on commands
        self.power_off_wl = ["power_off", "Power Off", "Power OFF"]  # whitelist for power off commands
        self.shutdown_wl = ["Graceful Shutdown", "shutdown", "graceful_shutdown"]  # whitelist for shutdown cmds

    def write_message_to_output(self, message, severity_level=SEVERITY_INFO):
        """
        Write a message to the output window\
        :param str message:  The message to be displayed in window
        :param integer severity_level: level of message, if == severity_error, colors red in window
        """
        if severity_level == SEVERITY_INFO:
            self.api_session.WriteMessageToReservationOutput(self.id, message)
        elif severity_level == SEVERITY_ERROR:
                self.api_session.WriteMessageToReservationOutput(self.id, '<font color="red">' + message + '</font>')

    def report_error(self, error_message, raise_error=True, write_to_output_window=False):
        """
        Report on an error to the log file, output window is optional.There is also an option to raise the error up
        :param str error_message:  The error message you would like to present
        :param bool raise_error:  Do you want to throw an exception
        :param bool write_to_output_window:  Would you like to write the message to the output window
        """
        self.logger.error(error_message)
        if write_to_output_window:
            self.write_message_to_output(error_message, SEVERITY_ERROR)
        if raise_error:
            raise QualiError(self.id, error_message)

    def report_info(self, message, write_to_output_window=False):
        """
        Report information to the log file, output window is optional.
        :param str message:  The message you would like to present
        :param bool write_to_output_window:  Would you like to write the message to the output window?
        """
        self.logger.info(message)
        if write_to_output_window:
            self.write_message_to_output(message, SEVERITY_INFO)

    def _item_in_list(self, i, l):
        """
        Returns Boolean if i in contained in l
        :param str i: the item to look for in the list
        :param list of str l: The list of items to look in
        :return: bool
        """
        try:
            idx = l.index(i)
            return True
        except:
            return False

    def _has_power_on(self, cmd_list):
        """
        Checks to see if the cmd_list contains one of the whitelisted power on commands
        returns command name if found, else ''
        :param cmd_list: list of str
        :return: str
        """
        cmd_name = ''
        for each in cmd_list:
            check = self._item_in_list(each.Name, self.power_on_wl)
            if check:
                cmd_name = each.Name
                break

        return cmd_name

    def _has_power_off(self, cmd_list):
        """
        Checks to see if the cmd_list contains one of the whitelisted power off commands
        return command name if found, else ''
        :param cmd_list: list of str
        :return: boolean
        """
        cmd_name = ''
        for each in cmd_list:
            check = self._item_in_list(each.Name, self.power_off_wl)
            if check:
                cmd_name = each.Name
                break

        return cmd_name

    def _has_shutdown(self, cmd_list):
        """
        Checks to see if the cmd_list contains one of the whitelisted shutdown commands
        returns command name if found, else ''
        :param cmd_list:
        :return:
        """
        cmd_name = ''
        for each in cmd_list:
            check = self._item_in_list(each.Name, self.shutdown_wl)
            if check:
                cmd_name = each.Name
                break

        return cmd_name

    def after_resources_changed(self, context, action_details, resources_details, service_details, removed_resources,
                                added_resources, modified_resources):
        """
        Intervene after a resource is added, removed, or has an attribute changed
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        :param str removed_resources: details about the removed resources
        :param str added_resources: details about the added resources
        :param str modified_resources: details about the modified resources
        """
        self.logger.info("AfterResourcesChanged called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)
        self.logger.info("added resources: " + added_resources)
        self.logger.info("removed resources: " + removed_resources)
        self.logger.info("modified resources: " + modified_resources)

        # actionDetails = ActionDetails(action_details)
        # resourcesDetails = ResourcesDetails(resources_details)
        # serviceDetails = ServiceDetails(service_details)
        addedResources = ResourcesDetails(added_resources)
        # removedResources = ResourcesDetails(removed_resources)
        # modifiedResources = ResourcesDetails(modified_resources)

        res_list = []
        for item in addedResources.resources:
            if '/' not in item.fullname:
                res_list.append(item.name)

        # for devices added, see if they have "Power ON" and call it
        # ##### DO POWER ON ###### #
        if len(res_list) > 0:
            try:
                for dev_name in res_list:
                    dev_cmd_list = self.api_session.GetResourceCommands(dev_name).Commands
                    dev_cmd_name = self._has_power_on(dev_cmd_list)
                    if dev_cmd_name != '':
                        # self.api_session.EnqueueResourceCommand(self.id, dev_name, dev_cmd_name)
                        # -- Old command for driver build commands only - updated is ExecuteCommand for all
                        self.api_session.EnqueueCommand(self.id, dev_name, 'Resource', dev_cmd_name)
                        self.report_info('Command "' + dev_cmd_name + '" called on ' + dev_name)

            except QualiError as qe:
                err = "Failed on AFTER RESOURCES CHANGED. " + str(qe)
                self.report_error(error_message=err, write_to_output_window=True)
            except:
                err = "Failed on AFTER RESOURCES CHANGED. Unexpected error: " + "'" + str(sys.exc_info()[0]) + "'"
                self.report_error(error_message=err, write_to_output_window=True)



    def before_resources_changed(self, context, action_details, resources_details, service_details, removed_resources,
                                 added_resources, modified_resources):
        """
        Intervene before a resource is added, removed, or has an attribute changed
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        :param str removed_resources: details about the removed resources
        :param str added_resources: details about the added resources
        :param str modified_resources: details about the modified resources
        """
        self.logger.info("BeforeResourcesChanged called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)
        self.logger.info("added resources: " + added_resources)
        self.logger.info("removed resources: " + removed_resources)
        self.logger.info("modified resources: " + modified_resources)

        # actionDetails = ActionDetails(action_details)
        # resourcesDetails = ResourcesDetails(resources_details)
        # serviceDetails = ServiceDetails(service_details)
        # addedResources = ResourcesDetails(added_resources)
        removedResources = ResourcesDetails(removed_resources)
        # modifiedResources = ResourcesDetails(modified_resources)

        res_list = []
        for item in removedResources.resources:
            if '/' not in item.fullname:
                res_list.append(item.name)

        # for devices being removed, check for Shutdown, then power off, call if it has one
        # ##### DO POWER OFF ###### #
        if len(res_list) > 0:
            try:
                for dev_name in res_list:
                    dev_cmd_list = self.api_session.GetResourceCommands(dev_name).Commands
                    dev_cmd_name = self._has_shutdown(dev_cmd_list)
                    if dev_cmd_name == '':
                        dev_cmd_name = self._has_power_off(dev_cmd_list)
                    if dev_cmd_name != '':
                        # self.api_session.EnqueueResourceCommand(self.id, dev_name, dev_cmd_name)
                        # -- Old command for driver build commands only - updated is ExecuteCommand for all
                        # self.api_session.EnqueueCommand(self.id, dev_name, 'Resource', dev_cmd_name)
                        # use Execute instead of Enqueue because it's called from a 'Sync' -
                        # sync can't complete till this is done.
                        self.api_session.ExecuteCommand(self.id, dev_name, 'Resource', dev_cmd_name)
                        self.report_info('Command "' + dev_cmd_name + '" called on ' + dev_name)
            except QualiError as qe:
                err = "Failed on BEFORE RESOURCES CHANGED. " + str(qe)
                self.report_error(error_message=err, write_to_output_window=True)
            except:
                err = "Failed on BEFORE RESOURCES CHANGED. Unexpected error: " + "'" + str(sys.exc_info()[0]) + "'"
                self.report_error(error_message=err, write_to_output_window=True)
