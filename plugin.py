# Woonveilig Gate01 Domoticz Plugin
# Author: Steven van den Beemt
#
"""
<plugin key="Woonveilig" name="Woonveilig Gate01" author="Steven van den Beemt" version="1.0.0" wikilink="" externallink="https://www.woonveilig.nl">
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default=""/>
        <param field="Username" label="Username" width="150px" required="true" default=""/>
        <param field="Password" label="Password" width="150px" required="true" default=""/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug" default="true"/>
                <option label="False" value="Normal" />
            </options>
        </param>
    </params>
</plugin>
"""
import sys
sys.path.append('/usr/local/lib/python3.4/dist-packages')

import Domoticz
import demjson
import urllib.request
import base64

class BasePlugin:

    def __init__(self):
        #self.var = 123
        return

    def onStart(self):
        Domoticz.Log("onStart called")       
        if (Parameters["Mode6"] == "Debug"):
            Domoticz.Debugging(1)

        if (len(Devices) == 0):

            url = "http://%s/action/sensorListGet" % Parameters["Address"]    
            response = MakeRequest(url)
            Domoticz.Log(response)
            data = ParseJson(response);

            for sensor in data["senrows"]:
                if (sensor["type"] == "Door Contact"): 
                    Domoticz.Device(Name=sensor["name"], TypeName="Switch", Switchtype=11, Unit=int(sensor["no"])).Create()
                if (sensor["type"] == "Remote Keypad"):
                    Options = {"LevelActions": "||","LevelNames": "Off|Home|On","LevelOffHidden": "false","SelectorStyle": "1"}
                    Domoticz.Device(Name=sensor["name"], Unit=99, TypeName="Selector Switch", Switchtype=18, Image=13, Options=Options).Create()

            Domoticz.Log("Devices created.")

        DumpConfigToLog()


    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data, Status, Extra):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

        Command = Command.strip()
        action, sep, params = Command.partition(' ')
        action = action.capitalize()

        if (Unit == 99): #=Remote Keypad
            #Now set the correct mode. 
            #Support for translating selector switch level to action
            if (action == 'Set'):
                if (params.capitalize() == 'Level'):   
                    if (Level == 10):
                        status = AlarmStatus.Home
                    elif (Level == 20):
                        status = AlarmStatus.On         
            if (action == 'Off'):
                status = AlarmStatus.Off
            elif (action == 'Home'):
                status = AlarmStatus.Home
            elif (action == 'On'):
                status = AlarmStatus.On

            url = "http://%s/action/panelCondPost" % Parameters["Address"]
            data = {"area" : 1, "mode" : status.value }
            response = MakeRequest(url,"POST",data)
            nValue = GetAlarmLevel(status) #convert to level: 0,10,20
            UpdateDevice(Unit=99, nValue = nValue, sValue= str(nValue))
            #Domoticz.Log(response)


    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")

        #1. Update status of Door contacts
        url = "http://%s/action/sensorListGet" % Parameters["Address"]    
        response = MakeRequest(url)
        #Domoticz.Log(response)
        data = ParseJson(response)
        for sensor in data["senrows"]:
                if (sensor["type"] == "Door Contact"): 
                    UpdateDevice(int(sensor["no"]), nValue = 1 if sensor["cond"] == "Open" else 0, sValue = "True" if sensor["cond"] == "Open" else "False")

        #2. Update status of alarm/remote keypad
        url = "http://%s/action/panelCondGet" % Parameters["Address"]
        response = MakeRequest(url)
        #Domoticz.Log(response)
        data = ParseJson(response)
        status = GetAlarmStatus(data["updates"]["mode_a1"]) #convert to enum status
        nValue = GetAlarmLevel(status) #convert to level: 0, 10, 20

        UpdateDevice(Unit=99, nValue = nValue, sValue= str(nValue))



global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Status, Connection, Description):
    global _plugin
    _plugin.onConnect(Status, Connection, Description)

def onMessage(Data, Connection, Status, Extra):
    global _plugin
    _plugin.onMessage(Data, Connection, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def ParseJson(crapyy_json):   
    crapyy_json = crapyy_json.replace("/*-secure-","")
    crapyy_json = crapyy_json.replace("*/","")
    data = demjson.decode(crapyy_json) 
    return data;

def MakeRequest(url, method="GET", data={}):
    credentials = base64.b64encode("{0}:{1}".format(Parameters["Username"], Parameters["Password"]).encode()).decode("ascii")
    headers = {'Authorization': "Basic " + credentials}
    data = urllib.parse.urlencode(data).encode()
    request = RESTRequest(url=url, headers=headers, data=data, method=method)
    connection = urllib.request.urlopen(request)
    response = connection.read().decode('utf-8')
    return response

def UpdateDevice(Unit, nValue, sValue):
# Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return

def GetAlarmLevel(status):
    if status == AlarmStatus.Off:
        return 0
    elif status == AlarmStatus.Home:
        return 10
    elif status == AlarmStatus.On:
        return 20

def GetAlarmStatus(status):
    if status == "Disarm":
        return AlarmStatus.Off
    elif status == "Arm":
        return AlarmStatus.On
    elif status == "Home":
        return AlarmStatus.Home

class RESTRequest(urllib.request.Request):
    __method = None

    def __init__(self, url, data=None, headers={}, origin_req_host=None, unverifiable=False, method=None):
        super().__init__(url, data, headers, origin_req_host, unverifiable)
        self.__method = method

    def get_method(self):

        # Uses the standard method choosing logic if no other method has been
        # explicitly set.

        if self.__method is None:
            return super().get_method()
        else:
            return self.__method


from enum import Enum
class AlarmStatus(Enum):
    Off = 4
    Home = 1
    On = 0