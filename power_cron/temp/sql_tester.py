import pymssql

connection = pymssql.connect('10.14.2.168', 'Dennis', 'Password1', 'DELL_CUSTOM_REPORTING')
cursor = connection.cursor()
# cursor.executemany("INSERT INTO [DELL_RESOURCES_POWER] VALUES (%s, %s, %s, %s, %s, %s, %s)",
#                [('2017-01-10 17:00:00.000', 'rr-kimo-10', 'OFF', 'PASS', 'Not Reserved', 'TRUE', '0.66')])

my_list = ['2017-01-10 17:15:00.000', 'rr-kimo-10', 'OFF', 'PASS', 'TRUE', 'FALSE', '0.77']
temp = "INSERT INTO [DELL_RESOURCES_POWER] VALUES ("
for idx in xrange(len(my_list)):
    temp += ("'" + my_list[idx] + "', ")

cursor.execute(temp)

connection.commit()
# print 'stop'
connection.close()


my_list = ['Dog', 'Cat', 'Bird', 'Fish']

check = (len(my_list) - 1)
print check

my_str = 'My List is: '
for i in xrange(len(my_list)):
	if i < check:
		my_str += (my_list[i] + ', ' )
	else:
		my_str += my_list[i]

print my_str
