from power_audit import PowerAudit


def main():
    print '\n\nManual Power Audit Verification'
    local = PowerAudit()

    audit_list = []
    loop_check = True
    temp = ''
    for fam in local.configs['target_family_list']:
        temp += '%s ' % fam

    print ' > %s' % local._get_dts()
    print 'Connected to %s\n' % local.configs['qs_server_hostname']
    print '\nResources from the following families are available to Audit:'
    print temp
    print '\nPlease Enter the full name of each device you which to Audit'
    print "  Enter 'blank' or DONE when complete"
    print '%s' % ('='*40)

    while loop_check:
        user_input = raw_input('Device Name: ')
        if user_input == '' or user_input.upper() == 'DONE':
            loop_check = False
        else:
            if local.resource_exists(user_input):
                audit_list.append(user_input)
            else:
                print "Resource '%s' does not exist - please verify name" % user_input
    #  end while

    if len(audit_list) >= 1:
        local.select_audit(device_list=audit_list)
    else:
        print 'You entered no valid devices, Terminating'

if __name__ == '__main__':
    main()
