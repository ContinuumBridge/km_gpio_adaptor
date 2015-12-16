#!/usr/bin/env python

ModuleName = "km_gpio_adaptor"
import sys
import time
import os
from gpio import KitchenMinderInputs
from sets import Set
from cbcommslib import CbAdaptor
from cbconfig import *
from twisted.internet import threads
from twisted.internet import reactor

class Adaptor(CbAdaptor):
    def __init__(self, argv):
        self.status = "ok"
        self.state = "stopped"
        self.inputs = KitchenMinderInputs()
        self.inputs.setupSwitch(self.switchPressed)
        self.inputs.setupPIR(self.movementDetected)
        self.apps =             {"binary_sensor": [],
                                 "gpio": []}
        CbAdaptor.__init__(self, argv)

    def switchPressed(self, channel):
        reactor.callFromThread(self.sendEvent, 'button')

    def movementDetected(self, channel):
        reactor.callFromThread(self.sendEvent, 'movement')

    def setState(self, state):
        self.state = state
        self.cbLog("debug", "state = " +  self.state)
        msg = {"id": self.id,
               "status": "state",
               "state": self.state}
        self.sendManagerMessage(msg)

    def onStop(self):
        self.inputs.cleanup()

    def sendEvent(self, e):
        self.cbLog("debug", "sendEvent, event: " + str(e))
        msg = {"id": self.id,
                "content": "characteristic",
                "characteristic": "gpio",
                "data": e,
                "timeStamp": time.time()
        }
        for a in self.apps["gpio"]:
            self.sendMessage(msg, a)
        if e == "movement":
            msg = {"id": self.id,
                   "content": "characteristic",
                   "characteristic": "binary_sensor",
                   "data": "on",
                   "timeStamp": time.time()
                  }
            for a in self.apps["binary_sensor"]:
                self.sendMessage(msg, a)
    
    def onAppInit(self, message):
        self.cbLog("debug", "onAppInit, req = " + str(message))
        resp = {"name": self.name,
                "id": self.id,
                "status": "ok",
                "service": [{"characteristic": "gpio"},
                            {"characteristic": "binary_sensor", "type": "gpio"}
                        ],
                "content": "service"}
        self.sendMessage(resp, message["id"])
        self.setState("running")

    def onAppRequest(self, message):
        # Switch off anything that already exists for this app
        for a in self.apps:
            if message["id"] in self.apps[a]:
                self.apps[a].remove(message["id"])
        # Now update details based on the message
        for f in message["service"]:
            if message["id"] not in self.apps[f["characteristic"]]:
                self.apps[f["characteristic"]].append(message["id"])

    def onAppCommand(self, message):
        self.cbLog("debug", "onAppCommand, message = " + str(message))

    def onConfigureMessage(self, config):
        """Config is based on what apps are to be connected.
        May be called again if there is a new configuration, which
        could be because a new app has been added.
        """
        self.cbLog("debug", "onConfigureMessage, config: " + str(config))
        self.setState("starting")

if __name__ == '__main__':
    adaptor = Adaptor(sys.argv)

