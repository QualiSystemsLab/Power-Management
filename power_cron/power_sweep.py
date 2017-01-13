import json
import logging
import base64
import time
import smtplib
import cloudshell.api.cloudshell_api as cs_api
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import random
import csv
import pymssql

LOG_DICT = {"DEBUG":10, "INFO":20, "WARNING":30, "WARN":30, "ERROR":40, "CRITICAL":50, "CRIT":50}
DAY_DICT = {"SUN":"SUNDAY", "MON":"MONDAY", "TUE":"TUESDAY", "WED":"WEDNESDAY", "THR":"THURSDAY", "FRI":"FRIDAY",
            "SAT":"SATURDAY"}
MAX_RESULTS = 5000

class power_sweep(object):

    def __init__(self):
        self.json_file_path = 'configs.json'
        self.configs = json.loads(open(self.json_file_path).read())

        # set logging
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                            filename=self.configs["logging_file_path"],
                            level=LOG_DICT[self.configs["logging_level"]])

        # get start time
        self.start_time = self._get_dts()
        self.end_time = ''
        logging.info('Script Started')

        self.headers = self.configs["report_headers"]

        #set the reporting location
        self.report_file = self.configs["report_file_path"] + "/" + self.configs["report_base_name"] + \
                           time.strftime('%Y_%m_%d_%H_%M')

        self.report_dts = time.strftime('%Y-%m-%d %H:%M:00')  # report 'date time stamp' used for all entries

        self.csv_file_path = self.configs["csv_folder"] + "/" + self.configs["who_am_i"] + "_" + \
            time.strftime('%Y_%m_%d_%H_%M') + '.csv'

        #build reporting matrix
        self.report_m = {}
        for each in self.headers:
            self.report_m[each] = []

        # shake the dice
        random.seed()

        # start CloudShell API Session
        try:
            self.cs_session = cs_api.CloudShellAPISession(self.configs["qs_server_hostname"],
                                                          self.configs["qs_admin_username"],
                                                          base64.b64decode(self.configs["qs_admin_password"]),
                                                          domain=self.configs["qs_cloudshell_domain"],port=8029)
            logging.info('Connected to CloudShell @ %s', self.configs["qs_server_hostname"])
        except:
            msg = self._get_dts() + '\n Critical Error connecting to CloudShell' + \
                  '\n' + self.configs["who_am_i"] + ' attempting to start CloudShell API Session' + \
                  '\nServer: ' + self.configs["qs_server_hostname"] + \
                  '\nPlease review logs'
            logging.critical('Unable to connect to CloudShell on Server: %s', self.configs["qs_server_hostname"])
            logging.debug('CloudShell Credentials: User= %s | Password= %s', self.configs["qs_admin_username"],
                          base64.b64decode(self.configs["qs_admin_password"]))
            logging.debug('CloudShell Domain: %s', self.configs["qs_cloudshell_domain"])
            self._send_email('Error connecting to CloudShell', msg, is_error=True)



    def _get_dts(self):
        return time.strftime('%Y-%m-%d %H:%M%:%S')

    def _send_email(self, subject, body, is_error=False):
        server = self.configs["smtp_server"]
        port = self.configs["smtp_port"]
        sender = self.configs["smtp_user"]
        if is_error:
            recipients = self.configs["email_error_reporting"]
            if self.configs["email_on_error_both"]:
                recipients += self.configs["email_standard_report"]
        else:
            recipients = self.configs["email_standard_report"]

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipients
        msg['Subject'] = subject
        message = body
        msg.attach(MIMEText(message))

        mailserver = smtplib.SMTP(server, port)
        # identify ourselves to smtp client
        mailserver.ehlo()
        # secure our email with tls encryption
        mailserver.starttls()
        # re-identify ourselves as an encrypted connection
        mailserver.ehlo()
        if self.configs["smpt_req_auth"]:
            mailserver.login(self.configs["smtp_user"],
                             base64.b64decode(self.configs["smtp_password"]))

        mailserver.sendmail(sender, recipients ,msg.as_string())

        mailserver.quit()


    def _append_report(self, col_header, value):
        """
        adds an entry to a report's specific column
        :param col_header:
        :param value:
        :return:
        """
        self.report_m[col_header].append(str(value))

    def _item_in_list(self, item, list):
        """
        returns the true if present, else false
        :param item: str
        :param list: list of str
        :return: Boolean
        """
        try:
            idx = list.index(item)
            return True
        except:
            return False

    def create_reservation(self):
        """
        Creates an immediate reservation and adds it to "self"
        :return: None
        """
        self.reservation = self.cs_session.CreateImmediateReservation(reservationName=self.configs["reservation_name"],
                                                                      owner=self.configs["qs_admin_username"],
                                                                      durationInMinutes=self.configs["reservation_duration"]
                                                                      ).Reservation
        self.res_id = self.reservation.Id
        logging.info('Created Reservation, ID: %s', self.res_id)
        logging.debug('Reservation Name: %s', self.configs["reservation_name"])
        logging.debug('Owner: %s', self.configs["qs_admin_username"])
        logging.debug('Start Time: %s', self.reservation.StartTime)
        logging.debug('End Time: %s', self.reservation.EndTime)

    def end_reservation(self):
        self.cs_session.EndReservation(self.res_id)

    def _get_resources_in_range(self, family):
        return self.cs_session.FindResourcesInTimeRange(resourceFamily=family,
                                                        untilTime=self.reservation.EndTime,
                                                        maxResults=MAX_RESULTS).Resources

    def build_resource_list(self):
        self.resource_list = []
        for each in self.configs["target_family_list"]:
            self.resource_list += self._get_resources_in_range(each)
            logging.info("Looked up items available from family %s", each)

    def _get_resource_list(self, family):
        return self.cs_session.FindResources(resourceFamily=family, maxResults=MAX_RESULTS).Resources

    def build_reporting_list(self):
        self.reporting_list = []
        for fam in self.configs["target_family_list"]:
            self.reporting_list += self._get_resource_list(fam)

    def get_resource_details(self, full_path):
        return self.cs_session.GetResourceDetails(full_path)


    def add_items_to_reservation(self, resource_full_path):
        self.cs_session.AddResourcesToReservation(self.res_id, [resource_full_path])
        logging.info("%s added to ResID %s", resource_full_path, self.res_id)

    def remove_item_from_reservation(self, resource_full_path):
        self.cs_session.RemoveResourcesFromReservation(self.res_id,[resource_full_path])
        logging.info('%s removed from ResId %s', resource_full_path, self.res_id)

    def _get_attribute_value(self, resource_full_path, attribute_name):
        val = ''
        att_list = []
        att_dict = self.cs_session.GetResourceDetails(resource_full_path).ResourceAttributes

        for each in att_dict:
            att_list.append(each.Name)

        if self._item_in_list(attribute_name, att_list):
            val = self.cs_session.GetAttributeValue(resource_full_path, attribute_name).Value

        return val

    def exclude_resource(self, resource_full_path):
        self.cs_session.ExcludeResource(resource_full_path)

    def include_resource(self, resource_full_path):
        self.cs_session.IncludeResource(resource_full_path)

    def hard_power_off(self, resource_full_path):
        self.cs_session.PowerOffResource(resourceFullPath=resource_full_path)

    def _has_shutdown(self, cmd_list):
        cmd_name = ''
        for each in cmd_list:
            check = self._item_in_list(each.Name, self.configs["device_shutdown_commands"])
            if check:
                cmd_name = each.Name
                break

        return cmd_name

    def _has_power_off(self, cmd_list):
        cmd_name = ''
        for each in cmd_list:
            check = self._item_in_list(each.Name, self.configs["device_power_off_commands"])
            if check:
                cmd_name = each.Name
                break

        return cmd_name

    def power_sweep_off(self, resource_full_path, resource_name):
        device_cmd_list = self.cs_session.GetResourceCommands(resource_full_path).Commands
        device_cmd = self._has_shutdown(device_cmd_list)

        if device_cmd == '' and self.configs["use_device_power_off"]:
            # if no shutdown cmd, see if it has a power off cmd
            device_cmd = self._has_power_off(device_cmd_list)

        if device_cmd != '':
            try:
                self.cs_session.ExecuteCommand(reservationId=self.res_id,
                                               targetName=resource_name,
                                               targetType='Resource',
                                               commandName=device_cmd)
                logging.info('%s command executed on %s', device_cmd, resource_name)
            except:
                logging.warning('Failed to execute %s on %s', device_cmd, resource_name)
        else:
            self.cs_session.SetAttributeValue(resourceFullPath=resource_full_path,
                                              attributeName=self.configs["audit_attribute_2"],
                                              attributeValue=self.configs["audit_attribute_2_fail"])

    def open_ms_sql_connection(self):
        try:
            self.sqlconn = pymssql.connect(host=self.configs["sql_server_address"],
                                           user=self.configs["sql_server_user"],
                                           password=base64.b64decode(self.configs["sql_server_password"]),
                                           database=self.configs["sql_database"])
            self.sql_cursor = self.sqlconn.cursor()
            self.sql_connection = True
        except Exception:
            pass

    def close_ms_sql_connection(self):
        if self.sql_connection:
            self.sqlconn.close()


    def open_csv(self):
        with open(self.csv_file_path, 'a') as self.csv_f:
            self.csvout = csv.writer(self.csv_f)


    def write_line_to_csv(self, line):
        # with open(self.csv_file_path, 'wb') as f:
        #     self.csvout = csv.writer(f)
        self.csvout.writerow(line)

    def close_csv(self):
        self.csv_f.close()


################################
def main():
    local = power_sweep()
    # local.create_reservation()
    # local.build_resource_list()
    #
    # # master loop to turn items off
    # for resource in local.resource_list:
    #     rand = random.random()
    #     path = resource.FullPath
    #     name = resource.FullName
    #     power_status = local._get_attribute_value(path, local.configs["audit_attribute_1"])
    #     control_status = local._get_attribute_value(path, local.configs["audit_attribute_2"])
    #
    #
    #     # debug logging
    #     logging.debug('Inspecting %s', resource.FullName)
    #     logging.debug('%s Value = %s', local.configs["audit_attribute_1"], power_status)
    #     logging.debug('%s Value = %s', local.configs["audit_attribute_2"], control_status)
    #     logging.debug('Random Number = %s', str(rand))
    #
    #     # if it's already off, try to turn some off anyway (5%)
    #     if power_status  == 'OFF' and rand <= local.configs["audit_gate_attribute_1"]:
    #         local.exclude_resource(path)
    #         local.hard_power_off(path)
    #         local.include_resource(path)
    #         logging.info('Power Off via API called on: %s', name)
    #
    #     # I'm on and in a normal status - turn me off
    #     elif power_status == 'ON' and control_status == local.configs["audit_attribute_2_good"]:
    #         #add to reservation
    #         local.add_items_to_reservation(path)
    #         logging.info('%s Added to ResID: %s', path, local.res_id)
    #
    #         # call power off method
    #         local.power_sweep_off(path, name)
    #
    #     # I'm on and in a known bad status - random set try to turn off anyway
    #     elif power_status == 'ON' \
    #         and control_status == local.configs["audit_attribute_2_bad"] \
    #         and rand <= local.configs["audit_gate_attribute_2"]:
    #                     #add to reservation
    #         local.add_items_to_reservation(path)
    #         logging.info('%s Added to ResID: %s', path, local.res_id)
    #
    #         # call power off method
    #         local.power_sweep_off(path, name)
    #
    #     # I'm on and in a all other bad status - random set try to turn off anyway
    #     elif power_status == 'ON'\
    #         and not control_status == local.configs["audit_attribute_2_bad"] \
    #         and rand <= local.configs["audit_gate_default"]:
    #                     #add to reservation
    #         local.add_items_to_reservation(path)
    #         logging.info('%s Added to ResID: %s', path, local.res_id)
    #
    #         # call power off method
    #         local.power_sweep_off(path, name)
    #
    # # end master loop
    # local.end_reservation()  # immediately kill reservation releasing devices back to the pool

    # build a new complete list of devices and scrap power data
    local.build_reporting_list()

    # manual test option:
    # local.reporting_list = local.cs_session.FindResources(resourceFamily='Dell Switch Chassis',
    #                                                       resourceModel='Z9500',
    #                                                       maxResults=MAX_RESULTS).Resources

    for item in local.reporting_list:
        # for every item in the list generated by families, pull details
        details = local.get_resource_details(item.FullPath)

        # use details to find attributes that match the reporting headers and add them to the report
        # -- some special headers are handled first, nulls allowed
        # -- These may change based on the Headers used for reporting!!!  configs.json: reporting_headers
        for header in local.headers:
            current_attribute_value = ''  # set to null as default
            if header == 'Date':
                current_attribute_value = local.report_dts  # we use a fixed date time for all entries
            elif header == 'ResourceName':
                current_attribute_value = details.Name  # device name
            elif header == 'Reserved':
                current_attribute_value = item.ReservedStatus  # if it's reserved
            else:
                for attribute in details.ResourceAttributes:
                    if attribute.Name == header:
                        current_attribute_value = attribute.Value  # if found, override the default value

            local.report_m[header].append(current_attribute_value)

    # open SQL connection
    local.open_ms_sql_connection()

    # open csv file
    if local.configs["capture_csv"]:
        with open(local.csv_file_path, 'a') as f:
            csvout = csv.writer(f)
            csvout.writerow(local.headers)
            f.close()

    # run the length of the report_M (convert to a single list, line by line, write to csv file)
    # length = len(local.report_m['Date'])
    length = len(local.report_m[local.headers[0]])
    for idx in xrange(length):
        line = []
        for h in local.headers:
            temp = local.report_m[h]
            line.append(temp[idx])

        # print line

        # send to sql
        sql_line = 'INSERT INTO [' + local.configs["sql_table"] + '] VALUES ('
        check = (len(line) - 1)

        for i in xrange(len(line)):
            if i < check:
                temp = "'" + line[i] + "',"
            else:
                temp = "'" + line[i] + "'"

            sql_line += temp
        # end for loop

        sql_line += ')'  # close the sql line

        # write Entry to SQL DB
        # print sql_line
        local.sql_cursor.execute(sql_line)
        local.sqlconn.commit()

        # then send to csv to save
        if local.configs["capture_csv"]:
            with open(local.csv_file_path, 'a') as f:
                csvout = csv.writer(f)
                csvout.writerow(line)
                f.close()

    local.close_ms_sql_connection()
    local.end_time = local._get_dts()

    logging.debug('Start Time: %s', self.start_time)
    logging.debug('End Time: %s', self.end_time)

    my_lookup = local.cs_session.FindResources(attributeValues=[{'Name':'Power_Status', 'Value':'ON'}]).Resources
    # print 'stop here'

if __name__ == '__main__':
    main()


