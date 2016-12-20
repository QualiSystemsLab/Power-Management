from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.context import InitCommandContext, ResourceCommandContext
from event_handlers.connections import *
from event_handlers.reservations import *
from event_handlers.resources import *
from event_handlers.services import *
import cloudshell.api.cloudshell_api as cs_api


class PowerService (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self.logger = get_qs_logger("extensibility", "QS", "service")
        self.cs_session = None
        self.cs_token = ''

    def get_cs_session(self, server_address='localhost', res_domain='Global', admin_token=None):
        """
        starts a session to the CloudShell API
        :param str server_address: Address/Hostname of the CloudShell API
        :param str res_domain: Domain for the session to act (based on the reservation's domain)
        :param str admin_token: Admin login token, encrypted
        :return:
        """
        if not self.cs_session or admin_token != self.cs_token:
            self.cs_session = cs_api.CloudShellAPISession(server_address, domain=res_domain, token_id=admin_token)
            self.cs_token = admin_token
        return self.cs_session

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """

        pass

# <editor-fold desc="reservations event handlers">
#     def AfterReservationCreated(self, context, actionDetails, resourcesDetails, serviceDetails):
#         """
#         Intervene after a reservation was created
#         :param ResourceCommandContext context: the context the command runs on
#         :param str actionDetails: details about the action
#         :param str resourcesDetails: details about the resource
#         :param str serviceDetails: details about the service
#         """
#         # return ReservationEvents().after_reservation_created(context, actionDetails, resourcesDetails, serviceDetails)
#         pass
#
#     def AfterReservationExtended(self, context, actionDetails, resourcesDetails, serviceDetails, newEndTime):
#         """
#         Intervene after the end time of a reservation has been changed
#         :param ResourceCommandContext context: the context the command runs on
#         :param str actionDetails: details about the action
#         :param str resourcesDetails: details about the resource
#         :param str serviceDetails: details about the service
#         :param str newEndTime: new end time
#         """
#         # return ReservationEvents().after_reservation_extended(context, actionDetails, resourcesDetails, serviceDetails,
#         #                                                      newEndTime)
#         pass
#
#     def BeforeReservationExtended(self, context, actionDetails, resourcesDetails, serviceDetails, newEndTime):
#         """
#         Intervene before the end time of a reservation has been changed
#         :param ResourceCommandContext context: the context the command runs on
#         :param str actionDetails: details about the action
#         :param str resourcesDetails: details about the resource
#         :param str serviceDetails: details about the service
#         :param str newEndTime: new end time
#         """
#         # return ReservationEvents().before_reservation_extended(context, actionDetails, resourcesDetails, serviceDetails,
#         #                                                      newEndTime)
#         pass

    def BeforeReservationTerminated_Sync(self, context, actionDetails, resourcesDetails, serviceDetails):
        """
        Intervene before the reservation is ended manually by user, or enters reservation teardown (synchronous only)
        :param ResourceCommandContext context: the context the command runs on
        :param str actionDetails: details about the action
        :param str resourcesDetails: details about the resource
        :param str serviceDetails: details about the service
        """
        address = context.connectivity.server_address
        domain = context.reservation.domain
        token = context.connectivity.admin_auth_token
        return ReservationEvents(self.get_cs_session(address, domain, token), context.reservation.reservation_id).\
            before_reservation_terminated(context, actionDetails, resourcesDetails, serviceDetails)

        # return ReservationEvents().before_reservation_terminated(context, actionDetails, resourcesDetails, serviceDetails)

    def OnReservationStarted(self, context, resourcesDetails, serviceDetails):
        """
        Intervene after the reservation starts
        :param ResourceCommandContext context: the context the command runs on
        :param str resourcesDetails: details about the resource
        :param str serviceDetails: details about the service
        """

        address = context.connectivity.server_address
        domain = context.reservation.domain
        token = context.connectivity.admin_auth_token

        return ReservationEvents(self.get_cs_session(address, domain, token), context.reservation.reservation_id).\
            on_reservation_started(context, resourcesDetails, serviceDetails)

    # def OnReservationEnded_Sync(self, context, resourcesDetails, serviceDetails):
    #     """
    #     Intervene before the reservation end date expires (synchronous only)
    #     :param ResourceCommandContext context: the context the command runs on
    #     :param str resourcesDetails: details about the resource
    #     :param str serviceDetails: details about the service
    #     """
    #     pass

# </editor-fold>

# <editor-fold desc="connections">
#     def AfterConnectionsChanged(self, context, actionDetails, resourcesDetails, serviceDetails,
#                                 addedConnections, removedConnections):
#         """
#         Intervene after a logical connector has been added or removed in a reservation
#         :param ResourceCommandContext context: the context the command runs on
#         :param str actionDetails: details about the action
#         :param str resourcesDetails: details about the resource
#         :param str serviceDetails: details about the service
#         :param str addedConnections: details about the added connections
#         :param str removedConnections: details about the removed connections
#         """
#         return ConnectionEvents().after_connections_changed(context, actionDetails, resourcesDetails, serviceDetails,
#                                                             addedConnections, removedConnections)
#
#     def AfterMyConnectionsChanged(self, context, actionDetails, resourcesDetails, serviceDetails,
#                                   addedConnections, removedConnections):
#         """
#         Intervene after a logical connector has been added or removed to the service to which this driver is associated
#         :param ResourceCommandContext context: the context the command runs on
#         :param str actionDetails: details about the action
#         :param str resourcesDetails: details about the resource
#         :param str serviceDetails: details about the service
#         :param str addedConnections: details about the added connections
#         :param str removedConnections: details about the removed connections
#         """
#         return ConnectionEvents().after_my_connections_changed(context, actionDetails, resourcesDetails, serviceDetails,
#                                                                addedConnections, removedConnections)
#
#     def BeforeConnectionsChanged(self, context, actionDetails, resourcesDetails, serviceDetails,
#                                  addedConnections, removedConnections):
#         """
#         Intervene before a logical connector has been added or removed in a reservation
#         :param ResourceCommandContext context: the context the command runs on
#         :param str actionDetails: details about the action
#         :param str resourcesDetails: details about the resource
#         :param str serviceDetails: details about the service
#         :param str addedConnections: details about the added connections
#         :param str removedConnections: details about the removed connections
#         """
#         return ConnectionEvents().before_connections_changed(context, actionDetails, resourcesDetails, serviceDetails,
#                                                              addedConnections, removedConnections)
#
#     def BeforeMyConnectionsChanged(self, context, actionDetails, resourcesDetails, serviceDetails,
#                                    addedConnections, removedConnections):
#         """
#         Intervene before a logical connector has been added or removed to the service to which this driver is associated
#         :param ResourceCommandContext context: the context the command runs on
#         :param str actionDetails: details about the action
#         :param str resourcesDetails: details about the resource
#         :param str serviceDetails: details about the service
#         :param str addedConnections: details about the added connections
#         :param str removedConnections: details about the removed connections
#         """
#         return ConnectionEvents().before_my_connections_changed(context, actionDetails, resourcesDetails,
#                                                                 serviceDetails, addedConnections, removedConnections)
# </editor-fold>

# <editor-fold desc="resources">
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

        address = context.connectivity.server_address
        domain = context.reservation.domain
        token = context.connectivity.admin_auth_token
        return ResourcesEvents(self.get_cs_session(address, domain, token), context.reservation.reservation_id).\
            after_resources_changed(context, actionDetails, resourcesDetails,
                                    serviceDetails, resourcesRemoved, resourcesAdded, modifiedResources)

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

        address = context.connectivity.server_address
        domain = context.reservation.domain
        token = context.connectivity.admin_auth_token
        return ResourcesEvents(self.get_cs_session(address, domain, token), context.reservation.reservation_id).\
            before_resources_changed(context, actionDetails, resourcesDetails, serviceDetails, resourcesRemoved,
                                     resourcesAdded, resourcesModified)

# </editor-fold>

# <editor-fold desc="services">
#     def AfterServicesChanged(self, context, actionDetails, resourcesDetails, serviceDetails,
#                              oldServiceAttributeDetails, servicesRemoved, servicesAdded, modifiedServices,
#                              servicesModifiedAttributes):
#         """
#         Intervene after a service is added, removed, or has an attribute changed in reservation
#         :param ResourceCommandContext context: the context the command runs on
#         :param str actionDetails: details about the action
#         :param str resourcesDetails: details about the resource
#         :param str serviceDetails: details about the service
#         :param str oldServiceAttributeDetails: details about the service attributes before the changes
#         :param str servicesRemoved: details about the added services
#         :param str servicesAdded: details about the removed services
#         :param str modifiedServices: details about the modified services
#         :param str servicesModifiedAttributes: details about the service attributes after the changes
#         """
#         address = context.connectivity.server_address
#         domain = context.reservation.domain
#         token = context.connectivity.admin_auth_token
#         return ServicesEvents(self.get_cs_session(address, domain, token), context.reservation.reservation_id).\
#             after_services_changed(context, actionDetails, resourcesDetails, serviceDetails, oldServiceAttributeDetails,
#                                    servicesRemoved, servicesAdded, modifiedServices, servicesModifiedAttributes)
#
#     def BeforeServicesChanged_Sync(self, context, actionDetails, resourcesDetails, serviceDetails,
#                               oldServiceAttributeDetails, servicesRemoved, servicesAdded, modifiedServices,
#                               servicesModifiedAttributes):
#         """
#         Intervene before a service is added, removed, or has an attribute changed in reservation
#         :param ResourceCommandContext context: the context the command runs on
#         :param str actionDetails: details about the action
#         :param str resourcesDetails: details about the resource
#         :param str serviceDetails: details about the service
#         :param str oldServiceAttributeDetails: details about the service attributes before the changes
#         :param str servicesRemoved: details about the added services
#         :param str servicesAdded: details about the removed services
#         :param str modifiedServices: details about the modified services
#         :param str servicesModifiedAttributes: details about the service attributes after the changes
#         """
#         address = context.connectivity.server_address
#         domain = context.reservation.domain
#         token = context.connectivity.admin_auth_token
#         return ServicesEvents(self.get_cs_session(address, domain, token), context.reservation.reservation_id)\
#             .before_services_changed(context, actionDetails, resourcesDetails, serviceDetails,
#                                      oldServiceAttributeDetails, servicesRemoved, servicesAdded, modifiedServices,
#                                      servicesModifiedAttributes)
#
#     def BeforeMyServiceChanged_Sync(self, context, actionDetails, resourcesDetails, serviceDetails,
#                                     oldServiceAttributeDetails, servicesRemoved, servicesAdded, modifiedServices,
#                                     servicesModifiedAttributes):
#         """
#         Intervene before the service with which this driver is associated is added, removed, or has an attribute
#         changed in reservation
#         :param ResourceCommandContext context: the context the command runs on
#         :param str actionDetails: details about the action
#         :param str resourcesDetails: details about the resource
#         :param str serviceDetails: details about the service
#         :param str oldServiceAttributeDetails: details about the service attributes before the changes
#         :param str servicesRemoved: details about the added services
#         :param str servicesAdded: details about the removed services
#         :param str modifiedServices: details about the modified services
#         :param str servicesModifiedAttributes: details about the service attributes after the changes
#         """
#         address = context.connectivity.server_address
#         domain = context.reservation.domain
#         token = context.connectivity.admin_auth_token
#         return ServicesEvents(self.get_cs_session(address, domain, token), context.reservation.reservation_id).\
#             before_my_service_changed(context, actionDetails, resourcesDetails, serviceDetails,
#                                       oldServiceAttributeDetails, servicesRemoved, servicesAdded, modifiedServices,
#                                       servicesModifiedAttributes)
#
#     def BeforeServicesRemoved(self, context, actionDetails, resourcesDetails, serviceDetails,
#                               oldServiceAttributeDetails, servicesRemoved, servicesAdded, modifiedServices,
#                               servicesModifiedAttributes):
#         """
#         Intervene before a service is added, removed, or has an attribute changed in reservation
#         :param ResourceCommandContext context: the context the command runs on
#         :param str actionDetails: details about the action
#         :param str resourcesDetails: details about the resource
#         :param str serviceDetails: details about the service
#         :param str oldServiceAttributeDetails: details about the service attributes before the changes
#         :param str servicesRemoved: details about the added services
#         :param str servicesAdded: details about the removed services
#         :param str modifiedServices: details about the modified services
#         :param str servicesModifiedAttributes: details about the service attributes after the changes
#         """
#         address = context.connectivity.server_address
#         domain = context.reservation.domain
#         token = context.connectivity.admin_auth_token
#         return ServicesEvents(self.get_cs_session(address, domain, token), context.reservation.reservation_id).\
#             before_services_removed(context, actionDetails, resourcesDetails, serviceDetails,
#                                     oldServiceAttributeDetails, servicesRemoved, servicesAdded, modifiedServices,
#                                     servicesModifiedAttributes)
#
#     def BeforeMyServiceRemoved_Sync(self, context, actionDetails, resourcesDetails, serviceDetails,
#                                     oldServiceAttributeDetails, servicesRemoved, servicesAdded, modifiedServices,
#                                     servicesModifiedAttributes):
#         """
#         Intervene before the service with which this driver is associated is added, removed, or has an attribute
#         changed in reservation
#         :param ResourceCommandContext context: the context the command runs on
#         :param str actionDetails: details about the action
#         :param str resourcesDetails: details about the resource
#         :param str serviceDetails: details about the service
#         :param str oldServiceAttributeDetails: details about the service attributes before the changes
#         :param str servicesRemoved: details about the added services
#         :param str servicesAdded: details about the removed services
#         :param str modifiedServices: details about the modified services
#         :param str servicesModifiedAttributes: details about the service attributes after the changes
#         """
#         address = context.connectivity.server_address
#         domain = context.reservation.domain
#         token = context.connectivity.admin_auth_token
#         return ServicesEvents(self.get_cs_session(address, domain, token), context.reservation.reservation_id).\
#             before_my_service_removed(context, actionDetails, resourcesDetails, serviceDetails,
#                                       oldServiceAttributeDetails, servicesRemoved, servicesAdded, modifiedServices,
#                                       servicesModifiedAttributes)


    # </editor-fold>

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        self.cs_session.Logoff()
        self.cs_session = None
