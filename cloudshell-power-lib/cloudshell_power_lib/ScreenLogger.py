from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from cloudshell.shell.core.driver_context import ResourceCommandContext
import cloudshell.api.cloudshell_api as cs_api
import logging
# This include for functions that include this library
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

SCREEN_INFO = INFO + 1


# TODO There has to be a better way to do this whole file!
def add_screen_to_logger(logger, api_session, reservation_id):
    for handler in logger.handlers:
        if isinstance(handler, ReservationOutputHandler):
            handler.api_session = api_session
            handler.reservation_id = reservation_id
            return logger
    api_session = api_session
    reservation_id = reservation_id
    web_reservation_output_handler = ReservationOutputHandler(api_session, reservation_id)
    web_reservation_output_handler.setLevel(SCREEN_INFO)
    # web_reservation_output_handler.setFormatter(logging.Formatter('[%(levelname)s]: (%(funcName)-20s) %(message)s'))
    web_reservation_output_handler.setFormatter(logging.Formatter('PowerLib: %(message)s'))
    logger.addHandler(web_reservation_output_handler)

    # # Uncomment to print debugs to console
    # import sys
    # debug_handler = logging.StreamHandler(sys.stdout)
    # debug_handler.setLevel(SCREEN_INFO)
    # debug_handler.setFormatter(logging.Formatter('DBG--[%(levelname)s]: (%(funcName)-20s) %(message)s'))
    # logger.addHandler(debug_handler)

    return logger


def get_reservation_output_logger(context):
    """

    :param ResourceCommandContext context: the context the command runs on
    :return:
    """
    logger = LoggingSessionContext(context).get_logger_for_context(context)

    return add_screen_to_logger(logger, cs_api.CloudShellAPISession(
        context.connectivity.server_address,
        domain=context.reservation.domain,
        token_id=context.connectivity.admin_auth_token),
                                context.reservation.reservation_id)


class ReservationOutputHandler(logging.Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to the CloudShell reservation output window
    """

    def __init__(self, api_session=None, reservation_id=None):
        """
        Initialize the handler.

        """
        logging.Handler.__init__(self)
        self.api_session = api_session
        self.reservation_id = reservation_id

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the reservation Console window.
        """
        # try:
        #     msg = self.format(record)
        #     self.api_session.WriteMessageToReservationOutput(self.reservation_id,
        #                                                      msg)
        # # except (KeyboardInterrupt, SystemExit):
        # #    raise
        # # TODO: Needs review of how we handle these exceptions
        # except:
        #     self.handleError(record)
        msg = self.format(record)
        self.api_session.WriteMessageToReservationOutput(self.reservation_id,
                                                             msg)
