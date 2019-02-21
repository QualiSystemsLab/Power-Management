from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.api.common_cloudshell_api import CloudShellAPIError

import time

SEVERITY_INFO = 20
SEVERITY_ERROR = 40

NEXT_RESERVATION_ATTRIBUTE = 'Upcoming Reservation'  # attribute with a value for the forward looking reservations


class QualiError(Exception):
    def __init__(self, name, message):
        self.message = message
        self.name = name

    def __str__(self):
        return 'CloudShell error at ' + self.name + '. Error is:' + self.message


class NearTermReservations:
    def __init__(self, api_session, reservation_id):
        """
        :param CloudShellAPISession api_session: Active CloudShell API Connection
        :param string reservation_id: Current Context Reservation API
        """
        self.logger = get_qs_logger("extensibility", "QS", "service")
        self.api_session = api_session
        self.id = reservation_id
        self.who_am_i = 'near_term_reservations.py'

    def _check_upcoming_res_attribute(self, device_name):
        try:
            duration = self.api_session.GetAttributeValue(resourceFullPath=device_name,
                                                          attributeName=NEXT_RESERVATION_ATTRIBUTE).Value
            if duration > 0:
                check = True
            else:
                check = False
                if duration < 0:
                    duration = 0

            return check, duration

        except CloudShellAPIError as err:
            if 'Unable to locate' not in err.message:
                QualiError(self.who_am_i, err.message)  # handles an unknown error
            return False, 0

    def no_upcoming_reservations(self, device_name):
        check, value = self._check_upcoming_res_attribute(device_name)

        if check and value > 0:
            offset = (value * 60)  # assuming the offset is defined in minutes
            t1 = time.strftime('%d/%m/%Y %H:%M', time.localtime(time.mktime(time.localtime()) + time.timezone))
            t2 = time.strftime('%d/%m/%Y %H:%M', time.localtime(time.mktime(time.localtime()) + time.timezone + offset))
            r_list = self.api_session.GetResourceAvailabilityInTimeRange(resourcesNames=[device_name],
                                                                         startTime=t1,
                                                                         endTime=t2,
                                                                         showAllDomains=True).Resources
            len_check = 0
            for resource in r_list:
                for reservation in resource.Reservations:
                    if self.id != reservation.ReservationId:
                        len_check += 1

            if len_check == 0:
                return True
            else:
                return False

        else:
            return True
