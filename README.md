# Domoticz_Shelly_Plugin
Domoticz plugin for Shelly.

## Compability
Developed and tested with:
Shelly 1 with temperature Addon.
Shelly Plug.
Probably works with Shelly 1/PM but will not show wattage.

Tested on Rasbian Buster.
Domoticz:
Version: 2020.2
Python Version: 3.7.3 

## Futures
Reads switch state and optional temperature sensors.

## Support
Not likley.

# Usage
Create a folder "Shelly" in Domotics/Plugins and copy plugin.py there.

Restart Domoticz.

Add "Shelly" in the Hardware tab.


### Build Status
0.2.8 Initial release.

0.2.9 Switch on/off response was slow by design as I only check my switches for status, Response is now normal.
Thrown together with no respect at all for Python3 or standards.

Todo\:
- [ ] Cleanup code
- [x] Finish basic README
- [x] Initial upload
