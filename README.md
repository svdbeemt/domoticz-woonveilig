# Domoticz Woonveilig alarmsystem Plugin

This plugin will connect your Woonveilig Gate01 alarmsystem to Domoticz. This plugin was designed for using Domoticz as an addition on controlling the Woonveilig alarmsystem. No modifications to your Woonveilig configuration will be made.

The following Woonveilig accessories are supported and will automatically be installed as devices in Domoticz: 
* Door contacts
* Keypad

Currently IR sensors are not supported.

## Features
After installing the plugin you will be able to:
* Change the state of your alarm (arm, disarm, arm home)
* Door contact swtiches will be added. You can monitor when a door is open/closed and use this information for event based ruling.

## Installation and setup

If you are use a Raspberry Pi to host your Domoticz, you probably need to install libpython3.4 for plugins to work.
```
sudo apt install libpython3.4
```
At the moment of writing you also need to install:

```
sudo apt install python3-dev
sudo apt install python3-pip
sudo apt-get install python3-urllib3
sudo pip install demjson
```
In your domoticz/plugins directory do:
```
cd domoticz/plugins
git clone https://github.com/StuffNL/domoticz-woonveilig.git
```
Alternatively you can download the latest version from https://github.com/StuffNL/domoticz-woonveilig/archive/master.zip and unzip it. Then create a directory on your Domoticz device in domoticz/plugins named Woonvelig and transfer all the files to your device.

Restart your Domoticz service with:

```
sudo service domoticz.sh restart
```
Now go to Setup, Hardware in your Domoticz interface. There you add Woonveilig Gate01.

Make sure you enter all the required fields.

## Using the domoticz built-in security panel 
If you want to control the Woonvelig alarmsystem by using the built-in Domoticz Security panel you can achieve this by adding the following Event (LUA script):

Replace the values for variables `woonveiligKeypadDeviceName` and `domoticzSecurityPanelName` with your own devicenames.

```
commandArray = {}

woonveiligKeypadDeviceName = 'Alarm'
domoticzSecurityPanelName = 'Security Panel'

if (devicechanged[woonveiligKeypadDeviceName]) then
    
        print('**Update security status**')
        print(devicechanged[woonveiligKeypadDeviceName])

        if (devicechanged[woonveiligKeypadDeviceName] == 'Aan') then
                print('AlarmPanel Arm Away')
                commandArray[domoticzSecurityPanelName] = 'Arm Away'
        elseif (devicechanged[woonveiligKeypadDeviceName] == 'Thuis') then
                print('AlarmPanel Arm Home')
                commandArray[domoticzSecurityPanelName] = 'Arm Home'
        else
                print('AlarmPanel Disarm')
                commandArray[domoticzSecurityPanelName] = 'Disarm'
                commandArray['Keypad Ack'] = 'On'
        end
end

if (devicechanged['Security Panel']) then
    
        print('**Set Woonveilig Alarm**')
        print(devicechanged['Security Panel'])

        if (devicechanged[domoticzSecurityPanelName] == 'Arm Away' and otherdevices[woonveiligKeypadDeviceName] ~= 'Aan') then
                print('Woonveilig = Aan')
                commandArray[woonveiligKeypadDeviceName] = 'On'
        elseif (devicechanged[domoticzSecurityPanelName] == 'Arm Home' and otherdevices[woonveiligKeypadDeviceName] ~= 'Thuis') then
                print('Woonveilig = Thuis')
                commandArray[woonveiligKeypadDeviceName] = 'Home'
        elseif (devicechanged[domoticzSecurityPanelName] == 'Normal' and otherdevices[woonveiligKeypadDeviceName] ~= 'Uit') then
                print('Woonveilig = Uit')
                commandArray[woonveiligKeypadDeviceName] = 'Off'
        end
end

return commandArray

```
