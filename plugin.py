# Shelly1 example
#
# Author: Net-Time 2019
#
#
"""
<plugin key="Shelly" name="Shelly 1" author="Net-Time" version="0.2.9" wikilink="https://github.com/Net-time" externallink="https://www.Shelly.cloud">
    <description>
        <h2>Shelly 1, 1/PM with optional temperature probes</h2><br/>
        Checks a Shelly1 Status.
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="192.168.1.21"/>
        <param field="Mode2" label="Temp probes" width="75px">
            <options>
                <option label="0" value="0" default="true" />
                <option label="1" value="1" />
                <option label="2" value="2" />
                <option label="3" value="3" />
            </options> 
        </param>
        <param field="Mode3" label="Switch type" width="150px">
            <options>
                <option label="Switch" value="0" default="true" />
                <option label="Contact (Read only)" value="2" />
            </options> 
        </param>
        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import json

class BasePlugin:
    httpConn = None
    runAgain = 6
    disconnectCount = 0
    sProtocol = "HTTP"
    commandToSend = -1
    deviceOn = 1
    deviceOff = 0
    switchType = 0
   
    def __init__(self):
        return

    def onStart(self):
        if Parameters["Mode3"] == "2": # for some reason a contact is inverted vs a switch, go figure....
            self.switchType = 2
            self.deviceOn = 0
            self.deviceOff = 1
            
        if 1==1: #(Parameters["Mode4"] == "True"):
            if len(Devices)==0:
                    Domoticz.Device("Shelly", Unit=1, Type= 244, Subtype=62, Switchtype= self.switchType).Create()
                    Domoticz.Log("Created device: ")
        if Parameters["Mode2"] != "0": # Create temperature devices
                if len(Devices) != int(Parameters["Mode2"])+1:
                    for x in range(2,int(Parameters["Mode2"])+2):
                        Domoticz.Device("Shelly", Unit=x, Type= 80, Subtype=5).Create()
                        Domoticz.Log("Created device: ")
                        
        self.httpConn = Domoticz.Connection(Name=self.sProtocol+" Test", Transport="TCP/IP", Protocol=self.sProtocol, Address=Parameters["Address"], Port="80")
        self.httpConn.Connect()
        
    def onStop(self):
        Domoticz.Log("onStop - Plugin is stopping.")

    def onConnect(self, Connection, Status, Description):
        if (Status == 0):
            command = "/status" #Todo use /relay if no temp sensors
            if (self.commandToSend == 0):
                command = "/relay/0?turn=off"
                self.commandToSend=-1
            if (self.commandToSend == 1):
                command = "/relay/0?turn=on"
                self.commandToSend=-1
                
            VerBose("Shelly connected successfully." + command)
            sendData = { 'Verb' : 'GET',
                         'URL'  : command,
                         'Headers' : { 'Content-Type': 'text/xml; charset=utf-8', \
                                       'Connection': 'keep-alive', \
                                       'Accept': 'Content-Type: text/html; charset=UTF-8', \
                                       'Host': Parameters["Address"]+":"+ Parameters["Mode1"], \
                                       'User-Agent':'Domoticz/1.0' }
                       }
            Connection.Send(sendData)
        else:
            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Mode1"]+" with error: "+Description)

    def onMessage(self, Connection, Data):
        my_dict = json.loads( Data["Data"].decode("ascii", "ignore"))
        Status = int(Data["Status"])
        if (Status == 200):
            VerBose("Good Response received from Shelly")
            if "ison" in my_dict: # after a Domoticz switch state change we only get relay status
                relays_dict=my_dict
            else:
                relays_list =my_dict["relays"]
                relays_dict=relays_list[0]
            if "ext_temperature" in my_dict:
                temp_dict =my_dict["ext_temperature"]
                for x in range(2,int(Parameters["Mode2"])+2):
                    UpdateDevice(x,0,str(temp_dict[str(x-2)]["tC"]),0)
                    VerBose(str(x-2)+" Sensor " + str(temp_dict[str(x-2)]["tC"]))
        
            if (relays_dict["ison"]):
                VerBose("ON")
                UpdateDevice(1,self.deviceOn,"",0)
            else:
                VerBose("OFF")
                UpdateDevice(1,self.deviceOff,"",0)


        elif (Status == 302):
            Domoticz.Log("Shelly returned a Page Moved Error.")
        elif (Status == 400):
            Domoticz.Error("Shelly returned a Bad Request Error.")
        elif (Status == 500):
            Domoticz.Error("Shelly returned a Server Error.")
        else:
            Domoticz.Error("Shelly returned a status: "+str(Status))

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        if (Command == "On"):
            self.commandToSend=self.deviceOn
        else:
            self.commandToSend=self.deviceOff
        self.runAgain = 1
        onHeartbeat()
        
    def onDisconnect(self, Connection):
        return
        #Domoticz.Log("onDisconnect called for connection to: "+Connection.Address+":"+Connection.Port)

    def onHeartbeat(self):
        if (self.httpConn != None and (self.httpConn.Connecting() or self.httpConn.Connected())):
            Domoticz.Debug("onHeartbeat called, Connection is alive.")
        else:
            self.runAgain = self.runAgain - 1
            if self.runAgain <= 0:
                if (self.httpConn == None):
                    self.httpConn = Domoticz.Connection(Name=self.sProtocol+" Test", Transport="TCP/IP", Protocol=self.sProtocol, Address=Parameters["Address"], Port=Parameters["Mode1"])
                self.httpConn.Connect()
                self.runAgain = 6
            else:
                Domoticz.Debug("onHeartbeat called, run again in "+str(self.runAgain)+" heartbeats.")
                
def UpdateDevice(Unit, nValue, sValue, TimedOut):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue) or (Devices[Unit].TimedOut != TimedOut):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

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
def VerBose(text):
    if Parameters["Mode6"] != "0":
        Domoticz.Log(text)
    return
