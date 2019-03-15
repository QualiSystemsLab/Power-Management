# Power-Management Orchestration Scripts

## Power Setup 3.0
Custom setup script for Power Control capability
- (Disabled by default) Add Power Service if not in the reservation
- Power on all resources (based on PowerLib checks)

## Power Teardown 3.0
Custom Teardown script for Power Control capability
- Power off all resources (based on PowerLib checks)
NOTE: If you add any device configuration steps added to your teardown, be sure to add them to before_teardown_started
to avoid potential race conditions with the power-off

## Power On All
Orchestration script to power-on all resources in the reservation

## Power Off All
Orchestration script to power-off all resources in the reservation
