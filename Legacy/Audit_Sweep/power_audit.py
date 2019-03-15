import os
from subprocess import PIPE, Popen
import platform
import json
import logging
from base64 import b64decode
import time
import csv
import pymssql
import smtplib
from email.mime.text import MIMEText
import cloudshell.api.cloudshell_api as cs_api
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
# from cloudshell.cli.cli import CLI
import telnetlib

LOG_DICT = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "WARN": 30, "ERROR": 40, "CRITICAL": 50, "CRIT": 50}
DAY_DICT = {"SUN": "Sunday", "MON": "Monday", "TUE": "Tuesday", "WED": "Wednesday", "THR": "Thursday", "FRI": "Friday",
            "SAT": "Saturday"}
STATUS_ERROR_DICT = {'FAIL_UNKNOWN_PROMPT': '!-Verify Device Prompt  ',
                      'FAIL_SHUTDOWN_CHECK': '!-Verify Proper Shutdown  ',
                      'FAIL_MAPPING': '!-PDU Port not Mapped to Device  ',
                      'FAIL_NO_COMMAND': '!-No Power Commands  ',
                      'FAIL_CDU_COMMANDS': '!-Failure to run PDU Command',
                      'REQUIRES_CHECK': '!-Unknown Errors  ',
                      'FAIL_DEVICE_CONSOLE': '!-Console Connection Issues  '
                      }
ATTRIBUTUE_ERROR_DICT = {'PDU_Connected': '!-No Power Port on Device  ',
                          'Mgmt_IP_Pingable': '!-Unable to Ping Address  ',
                          'Console_IP_Pingable': '!-Unable to Ping Console IP  ',
                          'Console_Port_Status': '!-Unable to Connect via Console  '
                          }
DAY_HEADERS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
MAX_RESULTS = 5000
DELL_CONSOLE_ATT_NAME = 'Console IP'  # Networking Device Default should be 'Console Server IP Address'
DELL_CONSOLE_PORT_NAME = 'Console Port'  # Does currently follow the networking standard
DELL_PDU_STATUS_ATT = 'Power_Control_Status'


class PowerAudit(object):
    def __init__(self):
        self.who_am_i = ''
        self.resource_list = []
        self.connection_list = []
        self.reservation = None
        self.res_id = None
        self.attribute_count = 0
        self.audit_count = 0
        self.sql_connection = None
        self.summary_txt = ''
        self.cs_session = None
        self.reset_time = 0
        # open json config file
        # windows may need full path if on a remote disk
        # self.json_file_path = 'E:/path'   # manual set
        self.json_file_path = '{}/configs.json'.format(os.getcwd()).replace('\\', '/')  # manually set this
        self.configs = json.loads(open(self.json_file_path).read())

        self.res_duration = self.configs["reservation_duration"]

        self.dotw = time.strftime('%A')
        day_check = DAY_DICT.get(self.configs["full_audit_day"], 'ALL')
        if self.dotw == day_check or day_check == "ALL":
            self.audit_all = True
            self.res_duration = self.configs["full_audit_duration"]
        else:
            self.audit_all = False
            idx = 1
            self.audit_gate = {}
            for day in DAY_HEADERS:
                if day == DAY_DICT[self.configs["full_audit_day"]]:
                    self.audit_gate[day] = 0
                else:
                    self.audit_gate[day] = idx
                    if idx == self.configs["audit_rotation"]:
                        idx = 1
                    else:
                        idx += 1
            self.audit_check = self.audit_gate[self.dotw]

        # start logging
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                            filename=self.configs["logging_file_path"],
                            level=LOG_DICT[self.configs["logging_level"]])

        # get start time
        self.start_time = self._get_dts()
        self.end_time = ''
        logging.info('Script Started Successfully')

        self.report_dts = time.strftime('%Y-%m-%d %H:%M:00')  # report 'date time stamp' used for all entries

        self.email_time = time.strftime('%a, %d %b %Y')

        self.csv_file_path = self.configs["csv_folder"] + "/" + self.configs["who_am_i"] + "_" + \
                             time.strftime('%Y_%m_%d_%H_%M') + '.csv'

        self.boot_time = self.configs['boot_time_wait']
        # build reporting headers (based on BI Tracking)
        self.headers = self.configs["report_headers"]
        # build reporting matrix
        self.report_m = {}
        for each in self.headers:
            self.report_m[each] = []

        # build error matrix, for capturing failing devices
        # dict of list of list
        self.error_m = {}
        self._start_cloudshell_session()

    # end __init__

    def _start_cloudshell_session(self):
        # start CloudShell API Session
        self.cs_session = None
        try:
            self.cs_session = cs_api.CloudShellAPISession(self.configs["qs_server_hostname"],
                                                          self.configs["qs_admin_username"],
                                                          b64decode(self.configs["qs_admin_password"]),
                                                          domain=self.configs["qs_cloudshell_domain"], port=8029)
            logging.info('Connected to CloudShell @ %s', self.configs["qs_server_hostname"])
        except CloudShellAPIError as e:
            msg = self._get_dts() + '\n Critical Error connecting to CloudShell' + \
                  '\n' + self.configs["who_am_i"] + ' attempting to start CloudShell API Session' + \
                  '\nServer: ' + self.configs["qs_server_hostname"] + \
                  '\nPlease review logs'
            logging.critical('Unable to connect to CloudShell on Server: %s', self.configs["qs_server_hostname"])
            logging.critical(e.message)
            logging.debug(msg)
            logging.debug('CloudShell Credentials: User= %s | Password= %s', self.configs["qs_admin_username"],
                          b64decode(self.configs["qs_admin_password"]))
            logging.debug('CloudShell Domain: %s', self.configs["qs_cloudshell_domain"])
            self.send_email('Error connecting to CloudShell', msg)

    def _get_dts(self):
        return time.strftime('%Y-%m-%d %H:%M:%S')

    def send_email(self, subject='', message=''):
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = self.configs["smtp_user"]
        msg['To'] = self.configs["smtp_mail_list"]

        try:
            s = smtplib.SMTP(self.configs["smtp_server"], self.configs["smtp_port"])
            s.sendmail(self.configs["smtp_user"], self.configs["smtp_mail_list"], message)
            s.quit()
        except Exception as e:
            logging.warning('Unable to send email message')
            logging.warning(e.message)
            logging.warning(message)

    def create_resource_list(self):
        for fam in self.configs["target_family_list"]:
            logging.debug('Query FindResources Family:%s', fam)
            self.resource_list += self.cs_session.FindResources(resourceFamily=fam, maxResults=MAX_RESULTS).Resources

    def create_custom_resource_list(self, dev_name_list=[]):
        for name in dev_name_list:
            logging.debug('Adding %s to self.resource_list' % name)
            temp = self.cs_session.FindResources(resourceFullName=name).Resources
            for item in temp:
                if '/' not in item.FullName:
                    self.resource_list.append(item)

    def _has_attribute(self, resource_att_list, att_name):
        short_list = []
        for each in resource_att_list:
            short_list.append(each.Name)
        if att_name in short_list:
            return True
        else:
            return False

    def create_reservation(self):
        """
        Creates an immediate reservation and adds it to "self"
        This is the master reservation (self.res_id)
        :return: None
        """
        try:
            self.reservation = self.cs_session.CreateImmediateReservation(
                reservationName=self.configs["reservation_name"], owner=self.configs["qs_admin_username"],
                durationInMinutes=self.res_duration).Reservation

            self.res_id = self.reservation.Id
            logging.info('Created Reservation, ID: %s', self.res_id)
            logging.debug('Reservation Name: %s', self.configs["reservation_name"])
            logging.debug('Owner: %s', self.configs["qs_admin_username"])
            logging.debug('Start Time: %s', self.reservation.StartTime)
            logging.debug('End Time: %s', self.reservation.EndTime)
            # sleep for setup
        except CloudShellAPIError as e:
            self.res_id = None
            logging.debug('Unable to create a reservation')
            logging.critical('Error on CreateImmediateReservation: {}'.format(e.message))
            logging.debug('Reservation Name: {}  Owner: {}  Duration: {}'.format(self.configs["reservation_name"],
                                                                                 self.configs["qs_admin_username"],
                                                                                 self.res_duration))
        if self.res_id:
            time.sleep(15)
            self._clean_reservation()

    def _clean_reservation(self):
        """
        removes unwanted items that are automatically added to a reservation.
        :return:
        """
        # don't want any services in the reservation, like the power service
        res_details = self.cs_session.GetReservationDetails(self.res_id).ReservationDescription
        try:
            for service in res_details.Services:
                self.cs_session.RemoveServicesFromReservation(reservationId=self.res_id, services=[service.ServiceName])
                time.sleep(2)
        except CloudShellAPIError as e:
            logging.debug('self._clean_reservation: Trying to remove existing services from a fresh reservation')
            logging.error('Error on Clean Reservation: {}'.format(e.message))
            logging.debug('Reservation:{}, Services(list): {}'.format(self.res_id, res_details.Services))

    def end_reservation(self):
        self.cs_session.EndReservation(self.res_id)
        logging.info('Reservation %s ended' % self.res_id)

    def resource_exists(self, device_name):
        try:
            self.cs_session.GetResourceDetails(resourceFullPath=device_name).Address
            return True
        except CloudShellAPIError:
            return False

    def _connected_cmd_list(self, dev_name=''):
        cmd_list = []
        bulk = self.cs_session.GetResourceConnectedCommands(dev_name).Commands
        for each in bulk:
            cmd_list.append(each.Name)
        return cmd_list

    def _has_command(self, list_of_possibilities=[], list_of_commands=[]):
        result = ''
        temp = [i for i in list_of_possibilities if i in list_of_commands]
        if len(temp) > 0:
            result = temp[0]
        return result

    def power_on(self, device_name=''):
        cmds = self._connected_cmd_list(device_name)
        if self._has_command(list_of_possibilities=self.configs["power_on"], list_of_commands=cmds) != '':
            try:
                self.cs_session.PowerOnResource(reservationId=self.res_id, resourceFullPath=device_name)
                time.sleep(self.boot_time)  # let it boot up
                self.set_attribute_value(device_name, 'Power_Control_Status', 'PASS')  # set power good
            except CloudShellAPIError as e:
                self.set_attribute_value(device_name, 'Power_Control_Status', 'REQUIRES_CHECK')  # failed powering on
                logging.error(e.message)
        else:
            self.set_attribute_value(device_name, 'Power_Control_Status', 'FAIL_NO_COMMAND')
            logging.warn('%s does not have a power on connected command' % device_name)

    def power_off(self, device_name=''):
        cmds = self._connected_cmd_list(device_name)
        if self._has_command(list_of_possibilities=self.configs["power_off"], list_of_commands=cmds) != '':
            try:
                self.cs_session.PowerOffResource(reservationId=self.res_id, resourceFullPath=device_name)
            except CloudShellAPIError as e:
                logging.error(e.message)
        else:
            self.set_attribute_value(device_name, 'Power_Control_Status', 'FAIL_NO_COMMAND')  # fail powering off
            logging.warn('%s does not have a power off connected command' % device_name)

    def get_resource_details(self, full_path):
        """
        Queries for a full set of details about the device
        :param full_path:
        :return:
        """
        try:
            return self.cs_session.GetResourceDetails(full_path)
        except CloudShellAPIError as err:
            logging.warning(err.message)
            return None

    def add_to_reservation(self, device_name=''):
        try:
            self.cs_session.AddResourcesToReservation(reservationId=self.res_id, resourcesFullPath=[device_name])
            logging.debug('{} Added to Reservation'.format(device_name))
            time.sleep(2)  # adding a sleep here to make sure request is completed before moving on
        except CloudShellAPIError as err:
            logging.warning(err.message)

    def remove_from_reservation(self, device_name=''):
        try:
            self.cs_session.RemoveResourcesFromReservation(reservationId=self.res_id, resourcesFullPath=[device_name])
        except CloudShellAPIError as err:
            logging.warning(err.message)

    def get_attribute_value(self, dev_name, att_name):
        return self.cs_session.GetAttributeValue(resourceFullPath=dev_name, attributeName=att_name).Value

    def set_attribute_value(self, dev_name, att_name, value):
        try:
            self.cs_session.SetAttributeValue(resourceFullPath=dev_name, attributeName=att_name, attributeValue=value)
            logging.debug('Set %s Attribute %s to value of %s' % (dev_name, att_name, value))
        except CloudShellAPIError as err:
            logging.warning('Set Attribute Value >> Target:{}  Att:{} Value:{}'.format(dev_name, att_name, value))
            logging.warning(err.message)

    def is_available(self, dev_name):
        all_items = self.cs_session.GetResourceAvailability(resourcesNames=[dev_name]).Resources
        for each in all_items:
            if '/' not in each.Name:
                if len(each.Reservations) > 0:
                    return False
        return True

    def _has_pdu_connection(self, dev_name):
        children = self.cs_session.GetResourceDetails(resourceFullPath=dev_name).ChildResources
        for child in children:
            if ('Power Port' in child.Name) or ('PowerPort' in child.Name):
                if len(child.Connections) < 1:
                    self.set_attribute_value(dev_name=dev_name, att_name=DELL_PDU_STATUS_ATT, value='FAIL_MAPPING')
                    return False
                else:
                    return True
            else:
                return False

    def _cmdline(self, command):
        process = Popen(
            args=command,
            stdout=PIPE,
            shell=True
        )
        return process.communicate()[0]

    def _ping(self, address='8.8.8.8', count=1):
        check = False
        found = True
        packet_Tx = count
        pass_rate = 100

        my_plat = platform.system().lower()
        if my_plat == 'darwin':
            count_type = 'c'
        elif my_plat == 'win32' or my_plat == 'windows':
            count_type = 'n'
        else:
            count_type = 'c'

        raw = self._cmdline("ping -%s %s %s" % (count_type, packet_Tx, address))

        if 'timed' in raw or 'timeout' in raw:  # timed out is an autofail on a single ping
            logging.debug('Ping returned TIMEOUT')
        else:
            if 'unknown' not in raw and 'could not find' not in raw:  # is resolving
                if my_plat == 'darwin':
                    raw = raw.split('%')[0]
                    loss_rate = float(raw.split(' ')[-1])
                elif my_plat == 'win32' or my_plat == 'windows':
                    raw = raw.split('%')[0]
                    raw = raw.split(' ')[-1]
                    loss_rate = float(raw[1:])
                else:
                    raw = raw.split('%')[0]
                    loss_rate = float(raw.split(' ')[-1])

                packet_Rx = 100 - loss_rate

                if packet_Rx >= pass_rate:
                    check = True
                logging.info('Pinged %s packets - %s%s Received' % (packet_Tx, packet_Rx, '%'))
            else:  # doesn't resolve - fail and stop the recheck loop
                found = False
                logging.debug('Check Address, unable to find address to ping')

        return check, found

    def console_pingable(self, device_name='', console_ip_attribute_name=DELL_CONSOLE_ATT_NAME):
        try:
            console_ip = self.cs_session.GetAttributeValue(resourceFullPath=device_name,
                                                           attributeName=console_ip_attribute_name).Value
            return self._ping(address=console_ip)
        except Exception, e:
            logging.error('Error Pinging console (IP= %s) for %s' % (console_ip, device_name))
            logging.error('Console IP Attribute lookup: %s' % DELL_CONSOLE_ATT_NAME)
            logging.error(e.message)
            return False

    def device_pingable(self, device_name=''):
        final_check = False
        resolvable = True
        n = 0
        try:
            dev_address = self.cs_session.GetResourceDetails(resourceFullPath=device_name).Address
            while (n < 15) and (not final_check) and (resolvable):
                final_check, resolvable = self._ping(address=dev_address)
                n += 1
                if not final_check and resolvable and n < 15:
                    time.sleep(10)  # sleep only if false
        except Exception, e:
            logging.error('Error trying to ping %s' % device_name)
            logging.error(e.message)
        logging.debug('Pinged {} times - Final Result: {}'.format(n, final_check))
        return final_check

    def inspect_pdu_connected(self, device_name=''):
        # look to see if the device has a PDU Connection
        logging.info('Inspect PDU Connection started on %s' % device_name)
        details = self.cs_session.GetResourceDetails(resourceFullPath=device_name)
        pdu_att_name = self.configs["PDU_att_name"]
        if self._has_attribute(details.ResourceAttributes, pdu_att_name):
            if self._has_pdu_connection(device_name):
                self.set_attribute_value(device_name, pdu_att_name, 'TRUE')  # has a PDU attached
                return True
            else:
                self.set_attribute_value(device_name, pdu_att_name, 'FALSE')  # doesn't have a PDU attached
        else:
            logging.warning('No attribute named %s available on %s' % (pdu_att_name, device_name))  # bad news

        return False

    def _inner_connections(self, dev_details):
        # print dev_details.Name
        self.connection_list += dev_details.Connections
        for child in dev_details.ChildResources:
            self._inner_connections(child)

    def inspect_connections(self, device_name=''):
        logging.info('Inspect Connections started on %s' % device_name)
        self.connection_list = []
        has_reg_connections = False
        # self.child_count = 0
        details = self.cs_session.GetResourceDetails(resourceFullPath=device_name)
        self._inner_connections(details)

        # looks at if the device has data connections
        has_L1 = False
        sub_list = self.configs["L1_device_names"]
        if len(self.connection_list) > 0:
            has_reg_connections = True
            short_conn_list = []
            for single_conn in self.connection_list:
                short_conn_list.append(single_conn.FullPath)
            for sub in sub_list:
                if any(sub in string for string in short_conn_list):
                    has_L1 = True
                    break

            if has_L1:
                l1_count = 0
                for con_str in short_conn_list:
                    if sub in con_str:
                        l1_count += 1
                if l1_count == len(short_conn_list):
                    has_reg_connections = False
        con_att_name = self.configs['connections_att_name']
        if self._has_attribute(details.ResourceAttributes, con_att_name):  # has attribute check
            logging.debug('Setting value for %s on %s' % (con_att_name, device_name))
            if has_L1 and has_reg_connections:  # both L1 and non-L1 Connections
                self.set_attribute_value(device_name, con_att_name, 'L1_&_Direct')
            elif has_L1 and not has_reg_connections:  # L1 only
                self.set_attribute_value(device_name, con_att_name, 'L1')
            elif has_reg_connections:  # non-L1 Only
                self.set_attribute_value(device_name, con_att_name, 'Direct')
            else:  # non connections found
                self.set_attribute_value(device_name, con_att_name, 'NONE')
        else:
            logging.warning('No attribute named %s available on %s' % (con_att_name, device_name))  # bad news

        if has_L1 or has_reg_connections:
            return True

        return False

    def inspect_network_connectivity(self, device_name=''):
        logging.info('Inspect Network Connectivity called on %s' % device_name)
        details = self.cs_session.GetResourceDetails(resourceFullPath=device_name)
        network_check_name = self.configs['network_connect_att_name']
        if self._has_attribute(details.ResourceAttributes, network_check_name):
            if self.device_pingable(device_name=device_name):  # ping mgmt address
                self.set_attribute_value(device_name, network_check_name, 'PASS')
                return True
            else:
                self.set_attribute_value(device_name, network_check_name, 'FAIL')
        else:
            logging.warning('No Attribute named %s on %s' % (network_check_name, device_name))

        return False

    def inspect_console_connectivity(self, device_name=''):
        logging.info('Inspect Console Connectivity called on %s' % device_name)
        details = self.cs_session.GetResourceDetails(resourceFullPath=device_name)
        console_check_name = self.configs['console_connect_att_name']
        console_ip_att = self.configs['console_ip_att_name']
        if self._has_attribute(details.ResourceAttributes, console_check_name) and \
                self._has_attribute(details.ResourceAttributes, console_ip_att):  # has both attributes
            self.check_console_port(device_name=device_name)  # normalize to Dell Std
            if self.console_pingable(device_name=device_name):  # ping console IP
                self.set_attribute_value(device_name, console_check_name, 'PASS')
                return True
            else:
                self.set_attribute_value(device_name, console_check_name, 'FAIL')
                self.set_attribute_value(device_name, self.configs['console_port_connect_att_name'], 'FAIL')
                self.set_attribute_value(device_name, self.configs['prompt_att_name'], 'UNKNOWN')
        else:
            logging.warning('Missing of of the following attributes on %s or %s on %s' \
                            % (console_check_name, console_ip_att, device_name))
        return False

    def check_console_port(self, device_name=''):
        temp = self.get_attribute_value(device_name, DELL_CONSOLE_PORT_NAME)
        if temp != '':
            port = int(temp)
            if port < 100:
                port += 30000

            self.set_attribute_value(device_name, DELL_CONSOLE_PORT_NAME, str(port))
            logging.info('Fixed console port value, new value = %s on %s' % (port, device_name))
        else:
            port = -99
        return str(port)

    def _current_prompt(self, raw):
        if '\n' in raw:
            trash, good = raw.split('\n', 1)
        else:
            good = raw
        return good

    def check_prompt(self, device_name=''):
        logging.info('Check Prompt called on %s' % device_name)
        device_details = self.cs_session.GetResourceDetails(resourceFullPath=device_name)
        prompt_char = self.configs['prompt_chars']
        reg_ex_char = ''
        console_check = 'FAIL'
        for char in prompt_char:
            reg_ex_char += char

        if self._has_attribute(device_details.ResourceAttributes, DELL_CONSOLE_PORT_NAME) and \
                self._has_attribute(device_details.ResourceAttributes, DELL_CONSOLE_PORT_NAME):
            console_ip = self.get_attribute_value(device_name, DELL_CONSOLE_ATT_NAME)
            console_port = self.get_attribute_value(device_name, DELL_CONSOLE_PORT_NAME)

        try:
            tn = telnetlib.Telnet(host=console_ip, port=console_port)
            tn.write('\n')
            time.sleep(1)
            tn.write('\n')
            raw_output = tn.expect([r'%s' % reg_ex_char], 2)
            tn.close()
        except Exception as e:
            print e.message

        self.prompt = self._current_prompt(raw_output[2])
        self.prompt = self._current_prompt(self.prompt)

        if self.prompt != '':
            for char in prompt_char:
                if char in self.prompt:
                    self.prompt, trash = self.prompt.split(char, 1)
                    console_check = 'PASS'
                    break

        else:
            self.prompt = 'UNKNOWN'

        try:
            self.set_attribute_value(device_name, 'Console_Port_Status', console_check)
            self.set_attribute_value(device_name, 'Console_Prompt', self.prompt)
        except StandardError as e:
            logging.warning(e.message)

        return self.prompt

    def _open_ms_sql_connection(self):
        """
        Opens a session to the MS SQL Database where record keeping/reporting for power mgt is kept.
        """
        try:
            self.sqlconn = pymssql.connect(host=self.configs["sql_server_address"],
                                           user=self.configs["sql_server_user"],
                                           password=b64decode(self.configs["sql_server_password"]),
                                           database=self.configs["sql_database"])
            self.sql_cursor = self.sqlconn.cursor()
            self.sql_connection = True
            logging.info('MS SQL Connection Opened to: %s - Table %s', self.configs["sql_server_address"],
                         self.configs["sql_database"])
            logging.debug('MS SQL login %s:%s', self.configs["sql_server_user"],
                          b64decode(self.configs["sql_server_password"]))
        except StandardError as e:
            logging.critical('Failed to connect to MS SQL')
            logging.exception(e)
            logging.critical('MS SQL Connection Opened to: %s - Table', self.configs["sql_server_address"],
                             self.configs["sql_database"])
            logging.critical('MS SQL login %s:%s', self.configs["sql_server_user"],
                             b64decode(self.configs["sql_server_password"]))
            self.sql_connection = False

    def close_ms_sql_connection(self):
        """
        Closes the previously opened connection to MS SQL
        """
        if self.sql_connection:
            self.sqlconn.close()

    def _is_flagged(self, att_dict={}):
        # will have to be customized based on the headers and what good or bad values are
        for key in att_dict:
            if att_dict[key] == 'FAIL' or att_dict[key] == 'FALSE':
                return True
        return False

    def attribute_scrape(self, device_name):
        logging.info('Attribute Scrape called on %s ' % device_name)
        self.attribute_count += 1
        details = self.get_resource_details(device_name)
        if details:
            pdu_connection_bad = False
            current_values = {}
            for each in self.headers:
                current_values[each] = []

            for header in self.headers:
                temp_value = ''
                if header == 'Date':
                    temp_value = self.report_dts
                elif header == 'ResourceName':
                    temp_value = device_name
                elif header == 'Reserved':
                    if self.is_available(device_name):
                        temp_value = 'Not in Reservations'
                    else:
                        temp_value = 'Reserved'
                else:
                    if self._has_attribute(details.ResourceAttributes, header):
                        temp_value = self.get_attribute_value(device_name, header)

                self.report_m[header].append(temp_value)
                current_values[header] = temp_value
                logging.debug('data added to report_m %s:%s' % (header, temp_value))

            pdu_status_check = self.get_attribute_value(device_name, DELL_PDU_STATUS_ATT)
            if pdu_status_check != 'PASS' and pdu_status_check != 'NONE':
                pdu_connection_bad = True

            # -> add info to the error_m
            if self._is_flagged(att_dict=current_values) or pdu_connection_bad:
                rack_loc = current_values['Rack']  # based on how to group the reporting and is a header for the SQL Tbl
                if rack_loc not in self.error_m.keys():
                    self.error_m[rack_loc] = []  # if the key isn't there, add it to the dict.

                line = [rack_loc]
                console_ip_port = '%s:%s' % (self.get_attribute_value(device_name, DELL_CONSOLE_ATT_NAME),
                                             self.get_attribute_value(device_name, DELL_CONSOLE_PORT_NAME))
                temp_d = {'name': device_name,
                          'address': details.Address,
                          'console': console_ip_port,
                          'error': ''}

                for x_head in self.headers:
                    temp_error = ''
                    skip_list = ['Rack', 'Date', 'ResourceName', 'Reserved', 'Connections']
                    if x_head not in skip_list:  # yeah this would change base on the above block
                        # -> this is totally custom
                        header_value = current_values[x_head]
                        if header_value in ['FAIL', 'FALSE']:
                            temp_error += self._custom_att_error_flag(attribute_name=x_head)

                    if temp_error != '':
                        logging.debug('Attribute Error found on %s: %s' % (device_name, temp_error))

                    temp_d['error'] += temp_error

                if pdu_connection_bad:
                    temp_error = self._custom_pdu_status_error_flag(device_name)
                    temp_d['error'] += temp_error
                    logging.debug('PDU Status Error found on %s: %s' % (device_name, temp_error))

                # for key in temp_d.keys():
                #     line.append(temp_d[key])
                line.append(temp_d['name'])
                line.append(temp_d['address'])
                line.append(temp_d['console'])
                line.append(temp_d['error'])

                self.error_m[rack_loc].append(line)

            logging.debug('Attribute Scrape results: %s' % current_values)
        else:
            logging.warning('Skipped {} No Details available'.format(device_name))
        return current_values

    def _custom_att_error_flag(self, attribute_name):
        return ATTRIBUTUE_ERROR_DICT.get(attribute_name, '!-Unknown  ')

    def _custom_pdu_status_error_flag(self, dev_name):
        status = self.get_attribute_value(dev_name, DELL_PDU_STATUS_ATT)
        return STATUS_ERROR_DICT.get(status, 'NONE')

    def _send_report_to_sql(self):
        logging.debug('Sending report info to SQL')
        length = len(self.report_m[self.headers[0]])
        for idx in xrange(length):
            line = []
            for h in self.headers:
                temp = self.report_m[h]
                line.append(temp[idx])

            logging.debug('Report line generated %s', str(line))
            # send to SQL
            sql_line = 'INSERT INTO [%s] VALUES (' % self.configs['sql_table']
            check = (len(line) - 1)

            for i in xrange(len(line)):
                if i < check:
                    temp = "'%s'," % line[i]
                else:
                    temp = "'%s'" % line[i]

                sql_line += temp
            # end for loop

            sql_line += ')'  # close the sql line

            logging.debug('Built SQL Command')
            logging.debug(' - Source= %s', line)
            logging.debug(' - Result= %s', sql_line)

            # for debugging:
            # print line
            # print sql_line

            if not self.sql_connection:
                self._open_ms_sql_connection()

            if self.sql_connection:
                try:
                    self.sql_cursor.execute(sql_line)
                    self.sqlconn.commit()
                    logging.debug('MS SQL Cursor send: %s', sql_line)
                except StandardError as e:
                    logging.error('MS SQL Cursor Send Error %s' % sql_line)
                    logging.error(e)

    def send_report_to_csv(self):
        logging.info('Writing Report to CSV')
        with open(self.csv_file_path, 'ab') as f:
            csvout = csv.writer(f)
            csvout.writerow(self.headers)
            f.close()

        length = len(self.report_m[self.headers[0]])
        for idx in xrange(length):
            line = []
            for h in self.headers:
                temp = self.report_m[h]
                line.append(temp[idx])

            with open(self.csv_file_path, 'ab') as f:
                csvout = csv.writer(f)
                csvout.writerow(line)
                f.close()

    def write_to_summary(self):
        error_headers = ['Rack', 'Device Name', 'Address', 'Console Info', 'Error']  # info only - changed direction

        self.summary_txt += '%s Completed\n' % self.who_am_i
        self.summary_txt += 'Start Time: %s\n' % self.start_time
        self.summary_txt += '  End Time: %s\n' % self.end_time
        self.summary_txt += 'Reservation ID: %s\n' % self.res_id
        self.summary_txt += 'Num of Devices Audited: %s\n' % self.audit_count
        self.summary_txt += 'Attributes Captured On: %s\n' % self.attribute_count
        self.summary_txt += '\nErrors:\n'

        if len(self.error_m) > 0:
            sorted_keys = sorted(self.error_m.keys())
            self.summary_txt += 'Rack      Dev Name                 Address          ' + \
                                'Console Info           Error(s)\n'
            for key in sorted_keys:
                rack_list = self.error_m[key]
                for line in rack_list:
                    self.summary_txt += str(line[0]).ljust(10)
                    self.summary_txt += str(line[1]).ljust(25)
                    self.summary_txt += str(line[2]).ljust(17)
                    self.summary_txt += str(line[3]).ljust(23)
                    self.summary_txt += '%s\n' % line[4]
        else:
            self.summary_txt += '--None--\n'

        self.summary_txt += '=' * 95
        self.summary_txt += '\n\n'

        f = open(self.configs["summary_filepath"], 'a')
        f.write(self.summary_txt)
        f.close()

    def _audit_item(self, dev_name=''):
        # -> if available, add to reservation and update attributes via inspection
        if self.is_available(dev_name):
            logging.info('Auditing %s' % dev_name)
            self.audit_count += 1
            self.add_to_reservation(dev_name)
            try:
                has_pdu = self.inspect_pdu_connected(device_name=dev_name)
                if has_pdu:
                    # -> Power it on so we can look @ it
                    self.power_on(device_name=dev_name)  # may be powered on even if now PDU connection listed
                self.inspect_network_connectivity(device_name=dev_name)  # assuming that a device w/o PDU is ON
                self.inspect_connections(device_name=dev_name)
                if self.inspect_console_connectivity(device_name=dev_name):
                    self.check_prompt(device_name=dev_name)
                # ->now power off
                if has_pdu:
                    self.power_off(device_name=dev_name)
            except StandardError as err:
                logging.warning('Error in auditing {}'.format(dev_name))
                logging.warning(err.message)

            # take outta the reservation
            try:
                self.remove_from_reservation(device_name=dev_name)  # release it back to the pool
            except CloudShellAPIError as err:
                logging.warning(err.message)

    def _set_reset_time(self):
        self.reset_time = time.mktime(time.localtime()) + self.configs['session_reset_time']

    def _reservation_still_active(self, res_id):
        status = self.cs_session.GetReservationDetails(res_id).ReservationDescription.Status
        if status == 'Completed':
            return False
        else:
            return True

    def full_audit(self):
        self.who_am_i = 'Full Audit Sweep'
        logging.info('%s Started' % self.who_am_i)
        self.create_reservation()
        # build resource list
        if not self.res_id:
            logging.error('No Reservation ID, unable to continue')
        else:
            self.create_resource_list()
            self._set_reset_time()
            maxx = len(self.resource_list)
            loop_count = 0

            idx = 1
            for resource in self.resource_list:  # Main Loop
                if time.mktime(time.localtime()) > self.reset_time:  # checks for possible session timeout
                    self._start_cloudshell_session()
                    self._set_reset_time()
                try:
                    loop_count += 1
                    logging.info('Resource %s (%s of %s)' % (resource.Name, loop_count, maxx))
                    if self.audit_all or idx == self.audit_check:
                        # if it's a all audit day or the index matches today's number - audit the device
                        self._audit_item(dev_name=resource.Name)
                    if idx == self.configs["audit_rotation"]:
                        idx = 1
                    else:
                        idx += 1
                    # do attribute scrape for all devices (outside the reservation & inspection process)
                    self.attribute_scrape(device_name=resource.Name)
                except StandardError as err:
                    logging.warning(err.message)
                    self._start_cloudshell_session()  # in case of timeout

                # Check that Reservation is still running
                if not self._reservation_still_active(self.res_id):
                    logging.error('Reservation Shows Completed during process - Exiting >> ID: {}'.format(self.res_id))
                    break

            # end Main Loop

            # end reservation, done walking the list
            self.end_reservation()

            # sql dump of report_m
            self._send_report_to_sql()

            # optional csv capture
            if self.configs['capture_csv']:
                self.send_report_to_csv()

            # dump to summary
            self.end_time = self._get_dts()
            self.write_to_summary()

            if self.audit_all:
                # if it's the Audit All day, email the list of bad devices
                self.send_email(subject='%s Results for %s' % (self.who_am_i, self.report_dts),
                                message=self.summary_txt)

            self._send_report_to_sql()

    def select_audit(self, device_list=[]):
        """
        :param device_list: list of string  A list of the names of devices to inspect
        :return:
        """
        self.who_am_i = 'Select Item Audit'
        maxx = len(device_list)
        count = 0
        logging.debug('%s Started' % self.who_am_i)
        print '\n ******** \n'
        print '%s Starting Audit Run' % time.strftime('%H:%M:%S')
        print 'Creating Reservation'

        self.create_reservation()
        if not self.res_id:
            print '!! Reservation Not Created -- Unable to Continue'
        else:
            print '-- %s Reservation Created: %s' % (time.strftime('%H:%M:%S'), self.res_id)
            print 'Building Resource List'
            self.create_custom_resource_list(device_list)
            print '-- %s Resource List Built' % time.strftime('%H:%M:%S')
            for resource in self.resource_list:
                count += 1
                if self.is_available(resource.Name):
                    line = 'Auditing %s (%s of %s)' % (resource.Name, count, maxx)
                    print '-- %s %s' % (time.strftime('%H:%M:%S'), line)
                    logging.info(line)
                    self._audit_item(dev_name=resource.Name)
                    self.attribute_scrape(device_name=resource.Name)
                else:
                    line = '!! Unable to Audit %s - verify that the resource is available (%s of %s)' % (resource.Name,
                                                                                                         count, maxx)
                    print line
                    logging.info(line)

            # complete reservation
            self.end_reservation()

            # run summary
            self.end_time = self._get_dts()
            self.write_to_summary()

            print '\n ******** \n'
            print self.summary_txt
