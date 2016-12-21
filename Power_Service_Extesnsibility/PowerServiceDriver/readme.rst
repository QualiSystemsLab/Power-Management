
**Server Extensibility Using Cloudshell Services**

*Overview*
 
Using the new implementation of server side extension, it is now possible to call services in a reservation, whenever events occur on the reservation.
 
Administrators and power users can now create service drivers in Cloudshell Authoring, that will extend and define the behavior of Cloudshell reservations.
 
Example use cases:
Powering resources on when added to a reservation, or off when removed.
Sending an email when something changes in a reservation.
 
Note - you can have multiple service drivers in the same reservation, and each will be called when an event they implement is thrown. This means that you can have services handle different concerns in your reservation. 
 
Another feature introduced in this solution is Auto Add To Reservation. Services that are marked with an attribute will be added to any reservation that is starting. 
Organizations that want to implement a system-wide rule can combine Auto Add To Reservation & Extension For Service Drivers to add services that handle reservation events in all reservations.

**Disclaimer**

*Service drivers that handle events should be used with some care:*
 
1. Engineering discourages calling Testshell/CloudShell API from within your Service Driver to make changes to the reservation you are in. There are some  known critical issues for this usage depending on the specific method you use and your timing. Nevertheless, if your use case does require you to call Testshell API, please contact HQ to consult on how to implement your driver & test it.
 
2. For asynchronous commands, there is no promise that a command for an event that occurred earlier will be processed before an event that happened later, although it is likely.
 
3. Using synchronous commands to handle reservation events can have a high cost in performance and user experience (GUI can seem blocked). Try to avoid using synchronous commands to get the best performance and user experience.
 
4. Be sure to have enough spare capacity for commands in your Execution Server. Be sure that services models that handle events are set to "Supports Concurrent Commands"


**How it works**
 
Whenever events happen to a reservation, the extension will look at the services that are associated with that reservation and check if they have functions with specific known names.
In case a function with a known name exists, the service is considered subscribed to the event of the same name, and the function will be called whenever the event occurs.
 
The service command will be handled by your Execution Servers as usual, so make sure there is enough free capacity to handle your needs.
Also, the service model should be set to "Supports Concurrent Commands"

