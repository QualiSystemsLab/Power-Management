from input_converters import *
from cloudshell.shell.core.driver_context import ResourceCommandContext
from device_power_cmds import *

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
        self.device_pwr = device_power_mgmt(api_session, reservation_id)

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
            code = self.device_pwr.call_power_on(res_list)
            if code < 1:
                print "Error"

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
            code = self.device_pwr.call_power_off(res_list)
            if code < 1:
                print "Error"
