from input_converters import *
from cloudshell.shell.core.driver_context import ResourceCommandContext
from cloudshell.core.logger.qs_logger import get_qs_logger


class ReservationEvents:
    def __init__(self):
        self.logger = get_qs_logger("extensibility", "QS", "service")
        pass

    def after_reservation_created(self, context, action_details, resources_details, service_details):
        """
        Intervene after a reservation was created
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        """
        self.logger.info("AfterReservationCreated called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)

        actionDetails = ActionDetails(action_details)
        resourcesDetails = ResourcesDetails(resources_details)
        serviceDetails = ServiceDetails(service_details)
        pass

    def after_reservation_extended(self, context, action_details, resources_details, service_details, new_end_time):
        """
        Intervene after the end time of a reservation has been changed
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        :param str new_end_time: details about the service
        """
        self.logger.info("AfterReservationExtended called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)
        self.logger.info("new_end_time: " + new_end_time)

        actionDetails = ActionDetails(action_details)
        resourcesDetails = ResourcesDetails(resources_details)
        serviceDetails = ServiceDetails(service_details)

        pass


    def before_reservation_extended(self, context, action_details, resources_details, service_details, new_end_time):
        """
        Intervene before the end time of a reservation has been changed
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        :param str new_end_time: details about the service
        """
        self.logger.info("BeforeReservationExtended called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)
        self.logger.info("new_end_time: " + new_end_time)

        actionDetails = ActionDetails(action_details)
        resourcesDetails = ResourcesDetails(resources_details)
        serviceDetails = ServiceDetails(service_details)

        pass

    def before_reservation_terminated(self, context, action_details, resources_details, service_details):
        """
        Intervene before the reservation is ended manually by user, or enters reservation teardown (synchronous only)
        :param ResourceCommandContext context: the context the command runs on
        :param str action_details: details about the action
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        """
        self.logger.info("BeforeReservationTerminated called")
        self.logger.info("action details: " + action_details)
        self.logger.info("resources details: " + resources_details)
        self.logger.info("service details: " + service_details)

        actionDetails = ActionDetails(action_details)
        resourcesDetails = ResourcesDetails(resources_details)
        serviceDetails = ServiceDetails(service_details)
        pass

    def on_reservation_started(self, context, resources_details, service_details):
        """
        Intervene after the reservation starts
        :param ResourceCommandContext context: the context the command runs on
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        """
        self.logger.info("OnReservationStarted called")
        self.logger.info("resource details: " + resources_details)
        self.logger.info("service details: " + service_details)

        resourcesDetails = ResourcesDetails(resources_details)
        serviceDetails = ServiceDetails(service_details)
        pass

    def on_reservation_ended(self, context, resources_details, service_details):
        """
        Intervene before the reservation end date expires (synchronous only)
        :param ResourceCommandContext context: the context the command runs on
        :param str resources_details: details about the resource
        :param str service_details: details about the service
        """
        self.logger.info("OnReservationEnded called")
        self.logger.info("resource details: " + resources_details)
        self.logger.info("service details: " + service_details)

        resourcesDetails = ResourcesDetails(resources_details)
        serviceDetails = ServiceDetails(service_details)
        pass
