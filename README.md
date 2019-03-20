# Power Management
The power management system handles powering on/off resources automatically based on events during the reservation
lifecycle.
The primary benefit of this system is to decrease lab operational costs related to power &amp; cooling.

Tested with version 9.0 Patch 2; may work with other versions

## How it works

To enable power management, the resource should have a 'Power Management' attribute set to 'True' and have a power port
connected to a PDU resource. The power decision logic is recorded both in the log, as well as sent to the reservation's
output window.

Which events trigger power actions is based on the components you install. Please see the installation section for details.

### Power-on flow detail

    The resource must not be a sub-resource
    The Power Management attribute must be True
    The resource must not be shared
    There must be a 'PowerOn' command available to the resource
    The resource's 'PowerOn' command is called

### Power-off flow detail

    The resource must not be a sub-resource
    The Power Management attribute must be True
    The resource must not be shared
    There must be a 'PowerOn' command available to the resource
    The resource's 'PowerOn' command is called

## Installation instructions

### Components
* Power_Setup.zip - default Setup 3.0 script with additional step to power on all resources
* Power_Teardown.zip - default Teardown 3.0 script with additional step to power off all resources
* Power_off_All.zip - adds reservation command to 'Power off all'
* Power_on_All.zip - adds reservation command to 'Power on all'
* PowerServiceDriver.zip - Handles the use case of adding & removing resources while the reservation is active

### Orchestration scripts
To install the orchestration scripts (Power_Setup, Power_Teardown, Power_off_All, Power_on_All)
1. Log into CloudShell web UI
1. Navigate to 'Manage'->Scripts->Blueprint
1. If installing for the first time, drag the zip file into the browser window
1. If upgrading, mouse over the existing script and click the "three dots" drop down on the far right; select Edit and use the browse button to select and upload the updated zip file.

### Power Service
To install the power service
1. Log into CloudShell web UI
1. Navigate to 'Manage'->'Domains'->'Global'->'Services Categories'
1. Click 'add category to Domain' then 'Create new category'
1. Name the category 'Power' and hit 'Save'
1. Click your username and use 'Import Package' to select the PowerServiceDriver zip file.

## Debugging
Logs are located in the following location:
C:\ProgramData\QualiSystems\logs\<reservation ID>\<component>\*.log

### Common Errors
* "No power off or shutdown command available for resource"

    Make sure the resource is connected to a PDU with a 'PowerOff' command.

* "No power-on command available for resource"

    Make sure the resource is connected to a PDU with a 'PowerOn' command.

* "Can't power control shared resources"

    Un-share the resource before attempting to control power. If this message came during setup, you will need to
    un-share the resource in your source blueprint.

* "Power Management Attribute set to False"

    Modify the resource and set the 'Power Management' attribute to True

* "Power Management Attribute Not Found. Default to not controlling power"

    Add the 'Power Management' attribute to the resource's family and set the value to
    'True' for this specific resource.

## Source Details
### Orchestration
Scripts to power on/off resources from at reservation start/stop

### PowerServiceDriver
The Power Service
- Powers resources on when added to the reservation
- Powers resources off when removed from the reservation

### PowerLib
The common power library
