from input_converters import *
from cloudshell.shell.core.driver_context import ResourceCommandContext
from device_power_cmds import *


class ReservationEvents:
    def __init__(self, api_session, reservation_id):
        self.logger = get_qs_logger("extensibility", "QS", "service")
        self.device_pwr = device_power_mgmt(api_session, reservation_id)
        self.id = reservation_id
        self.api_session = api_session
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

        # actionDetails = ActionDetails(action_details)
        resourcesDetails = ResourcesDetails(resources_details)
        # servicesDetails = ServicesDetails(service_details)

        res_list = []
        for resource in resourcesDetails.resources:
            if '/' not in resource.fullname:
                res_list.append(resource.name)

        sev_list = []
        # for services in servicesDetails.services:
        #     if '/' not in services.alias:
        #         sev_list.append(services.alias)

        if len(res_list) > 0:
            return_code = self.device_pwr.call_power_off(res_list, "BEFORE RESERVATION TERMINATED")
            print return_code

        if len(sev_list) > 0:
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
        # servicesDetails = ServicesDetails(service_details)

        res_list = []
        for resource in resourcesDetails.resources:
            if '/' not in resource.fullname:
                res_list.append(resource.name)

        sev_list = []
        # for service in servicesDetails.services:
        #     sev_list.append(service.alias)

        # items added to reservation - do the power on
        if len(res_list) > 0:
            return_code = self.device_pwr.call_power_on(res_list, "ON RESERVATION STARTED")
            print return_code

        if len(sev_list) > 0:
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
        # servicesDetails = ServicesDetails(service_details)

        res_list = []
        for resource in resourcesDetails.resources:
            if '/' not in resource.fullname:
                res_list.append(resource.name)

        sev_list = []
        # for services in servicesDetails.services:
        #     if '/' not in services.alias:
        #         sev_list.append(services.alias)

        if len(res_list) > 0:
            # return_code = self.device_pwr.call_power_off(res_list, "ON RESERVATION ENDED")
            # print return_code
            pass

        if len(sev_list) > 0:
            pass
