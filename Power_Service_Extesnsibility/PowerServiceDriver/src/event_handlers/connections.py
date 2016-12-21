from input_converters import *
from cloudshell.shell.core.driver_context import ResourceCommandContext
from cloudshell.core.logger.qs_logger import get_qs_logger


class ConnectionEvents:
    def __init__(self):
        self.logger = get_qs_logger("extensibility", "QS", "service")
        pass

    def after_connections_changed(self, context, action_details, resources_details, service_details, added_connections,
                                  removed_connections):
        """
        Intervene after a logical connector has been added or removed in a reservation
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        :param str added_connections: details about the added connections
        :param str removed_connections: details about the removed connections
        """
        self.logger.info("AfterConnectionsChanged called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)
        self.logger.info("added connections: " + added_connections)
        self.logger.info("removed connections: " + removed_connections)

        actionDetails = ActionDetails(action_details)
        resourcesDetails = ResourcesDetails(resources_details)
        serviceDetails = ServiceDetails(service_details)
        addedConnections = ConnectionDetails(added_connections)
        removedConnection = ConnectionDetails(removed_connections)

        pass

    def after_my_connections_changed(self, context, action_details, resources_details, service_details,
                                     added_connections, removed_connections):
        """
        Intervene after a logical connector has been added or removed to the service to which this driver is associated
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        :param str added_connections: details about the added connections
        :param str removed_connections: details about the removed connections
        """
        self.logger.info("AfterMyConnectionsChanged called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)
        self.logger.info("added connections: " + added_connections)
        self.logger.info("removed connections: " + removed_connections)

        actionDetails = ActionDetails(action_details)
        resourcesDetails = ResourcesDetails(resources_details)
        serviceDetails = ServiceDetails(service_details)
        addedConnections = ConnectionDetails(added_connections)
        removedConnection = ConnectionDetails(removed_connections)

        pass

    def before_connections_changed(self, context, action_details, resources_details, service_details, added_connections,
                                   removed_connections):
        """
        Intervene before a logical connector has been added or removed in a reservation
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        :param str added_connections: details about the added connections
        :param str removed_connections: details about the removed connections
        """
        self.logger.info("BeforeConnectionsChanged called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)
        self.logger.info("added connections: " + added_connections)
        self.logger.info("removed connections: " + removed_connections)

        actionDetails = ActionDetails(action_details)
        resourcesDetails = ResourcesDetails(resources_details)
        serviceDetails = ServiceDetails(service_details)
        addedConnections = ConnectionDetails(added_connections)
        removedConnection = ConnectionDetails(removed_connections)

        pass

    def before_my_connections_changed(self, context, action_details, resources_details, service_details,
                                      added_connections, removed_connections):
        """
        Intervene before a logical connector has been added or removed to the service to which this driver is associated
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        :param str added_connections: details about the added connections
        :param str removed_connections: details about the removed connections
        """
        self.logger.info("BeforeMyConnectionsChanged called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)
        self.logger.info("added connections: " + added_connections)
        self.logger.info("removed connections: " + removed_connections)

        actionDetails = ActionDetails(action_details)
        resourcesDetails = ResourcesDetails(resources_details)
        serviceDetails = ServiceDetails(service_details)
        addedConnections = ConnectionDetails(added_connections)
        removedConnection = ConnectionDetails(removed_connections)

        pass
    