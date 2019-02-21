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


class ServicesEvents:
    def __init__(self, api_session, reservation_id):
        self.logger = get_qs_logger("extensibility", "QS", "service")
        self.api_session = api_session
        self.id = reservation_id

    def write_message_to_output(self, message, severity_level=SEVERITY_INFO):
        """
        Write a message to the output window
        :param str message:  the message to write to the output window
        :param integer severity_level:  Message level, if == severity_error, then message is displayed in red
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

    def after_services_changed(self, context, action_details, resources_details, service_details,
                               old_service_attributes_details, removed_services, added_services, modified_services,
                               services_modified_attributes):
        """
        Intervene after a service is added, removed, or has an attribute changed in reservation
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        :param str old_service_attributes_details: details about the service attributes before the changes
        :param str removed_services: details about the added services
        :param str added_services: details about the removed services
        :param str modified_services: details about the modified services
        :param str services_modified_attributes: details about the service attributes after the changes
        """
        self.logger.info("AfterServicesChanged called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)
        self.logger.info("added services: " + added_services)
        self.logger.info("removed services: " + removed_services)
        self.logger.info("modified services: " + modified_services)
        self.logger.info("old attributes (before change): " + old_service_attributes_details)
        self.logger.info("modified attributes (after change): " + services_modified_attributes)

        # actionDetails = ActionDetails(action_details)
        # resourcesDetails = ResourcesDetails(resources_details)
        # serviceDetails = ServiceDetails(service_details)
        addedServices = ResourcesDetails(added_services)
        # removedResources = ResourcesDetails(removed_services)
        # modifiedResources = ResourcesDetails(modified_services)
        # attributePrechange = AttributesDetails(old_service_attributes_details)
        # attributesPostChange = AttributesDetails(services_modified_attributes)

    def before_services_changed(self, context, action_details, resources_details, service_details,
                                old_service_attributes_details, removed_services, added_services, modified_services,
                                services_modified_attributes):
        """
        Intervene before a service is added, removed, or has an attribute changed in reservation
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        :param str old_service_attributes_details: details about the service attributes before the changes
        :param str removed_services: details about the added services
        :param str added_services: details about the removed services
        :param str modified_services: details about the modified services
        :param str services_modified_attributes: details about the service attributes after the changes
        """
        self.logger.info("AfterServicesChanged called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)
        self.logger.info("added services: " + added_services)
        self.logger.info("removed services: " + removed_services)
        self.logger.info("modified services: " + modified_services)
        self.logger.info("old attributes (before change): " + old_service_attributes_details)
        self.logger.info("modified attributes (after change): " + services_modified_attributes)

        # actionDetails = ActionDetails(action_details)
        # resourcesDetails = ResourcesDetails(resources_details)
        # serviceDetails = ServiceDetails(service_details)
        # addedResources = ResourcesDetails(added_services)
        removedServices = ResourcesDetails(removed_services)
        # modifiedResources = ResourcesDetails(modified_services)
        # attributePrechange = AttributesDetails(old_service_attributes_details)
        # attributesPostChange = AttributesDetails(services_modified_attributes)

    def before_my_service_changed(self, context, action_details, resources_details, service_details,
                                  old_service_attributes_details, removed_services, added_services, modified_services,
                                  services_modified_attributes):
        """
        Intervene before the service with which this driver is associated is added, removed, or has an attribute
        changed in reservation
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        :param str old_service_attributes_details: details about the service attributes before the changes
        :param str removed_services: details about the added services
        :param str added_services: details about the removed services
        :param str modified_services: details about the modified services
        :param str services_modified_attributes: details about the service attributes after the changes
        """
        self.logger.info("BeforeMyServiceChanged called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)
        self.logger.info("added services: " + added_services)
        self.logger.info("removed services: " + removed_services)
        self.logger.info("modified services: " + modified_services)
        self.logger.info("old attributes (before change): " + old_service_attributes_details)
        self.logger.info("modified attributes (after change): " + services_modified_attributes)

        actionDetails = ActionDetails(action_details)
        resourcesDetails = ResourcesDetails(resources_details)
        serviceDetails = ServiceDetails(service_details)
        addedResources = ResourcesDetails(added_services)
        removedResources = ResourcesDetails(removed_services)
        modifiedResources = ResourcesDetails(modified_services)
        attributePrechange = AttributesDetails(old_service_attributes_details)
        attributesPostChange = AttributesDetails(services_modified_attributes)

        pass

    def before_services_removed(self, context, action_details, resources_details, service_details,
                                old_service_attributes_details, removed_services, added_services, modified_services,
                                services_modified_attributes):
        """
        Intervene before a service removed in reservation
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        :param str old_service_attributes_details: details about the service attributes before the changes
        :param str removed_services: details about the added services
        :param str added_services: details about the removed services
        :param str modified_services: details about the modified services
        :param str services_modified_attributes: details about the service attributes after the changes
        """
        self.logger.info("BeforeServicesRemoved called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)
        self.logger.info("added services: " + added_services)
        self.logger.info("removed services: " + removed_services)
        self.logger.info("modified services: " + modified_services)
        self.logger.info("old attributes (before change): " + old_service_attributes_details)
        self.logger.info("modified attributes (after change): " + services_modified_attributes)

        actionDetails = ActionDetails(action_details)
        resourcesDetails = ResourcesDetails(resources_details)
        serviceDetails = ServiceDetails(service_details)
        addedResources = ResourcesDetails(added_services)
        removedResources = ResourcesDetails(removed_services)
        modifiedResources = ResourcesDetails(modified_services)
        attributePrechange = AttributesDetails(old_service_attributes_details)
        attributesPostChange = AttributesDetails(services_modified_attributes)

        pass

    def before_my_service_removed(self, context, action_details, resources_details, service_details,
                                  old_service_attributes_details, removed_services, added_services, modified_services,
                                  services_modified_attributes):
        """
        Intervene before the service with which this driver is associated is removed
        changed in reservation
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        :param str old_service_attributes_details: details about the service attributes before the changes
        :param str removed_services: details about the added services
        :param str added_services: details about the removed services
        :param str modified_services: details about the modified services
        :param str services_modified_attributes: details about the service attributes after the changes
        """
        self.logger.info("BeforeMyServiceRemoved called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)
        self.logger.info("added services: " + added_services)
        self.logger.info("removed services: " + removed_services)
        self.logger.info("modified services: " + modified_services)
        self.logger.info("old attributes (before change): " + old_service_attributes_details)
        self.logger.info("modified attributes (after change): " + services_modified_attributes)

        actionDetails = ActionDetails(action_details)
        resourcesDetails = ResourcesDetails(resources_details)
        serviceDetails = ServiceDetails(service_details)
        addedResources = ResourcesDetails(added_services)
        removedResources = ResourcesDetails(removed_services)
        modifiedResources = ResourcesDetails(modified_services)
        attributePrechange = AttributesDetails(old_service_attributes_details)
        attributesPostChange = AttributesDetails(services_modified_attributes)

        pass
