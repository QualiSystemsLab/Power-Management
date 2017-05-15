from power_audit import PowerAudit

my_count = 0
unit = PowerAudit()

device = 'bcm-z9000-1'
# unit.check_prompt(device)

# catch = unit._has_pdu_connection('st-sjc-s6000-6')

# unit.inspect_connections(device)
# for con in unit.connection_list:
#     print con.FullPath

# unit.attribute_scrape(device_name=device)
# for entry in unit.report_m:
#     print entry, unit.report_m[entry]

# unit.power_on(device)

# unit.full_audit()
# for entry in unit.report_m:
#     print entry, unit.report_m[entry]
# for error in unit.error_m:
#     print error, unit.error_m[error]

# my_msg = 'This is a test email'
# unit.send_email(my_msg)

result = unit.configs.get['logging_level', 'WARN']
print result
