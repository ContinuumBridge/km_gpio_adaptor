#!/usr/bin/env python

ModuleName = "km_gpio_adaptor"
import sys
import time
import os
import logging
from gpio import KitchenMinderInputs
from sets import Set
from cbcommslib import CbAdaptor
from cbconfig import *
from twisted.internet import threads
from twisted.internet import reactor

class Adaptor(CbAdaptor):
    def __init__(self, argv):
        logging.basicConfig(filename=CB_LOGFILE,level=CB_LOGGING_LEVEL,format='%(asctime)s %(message)s')
        self.status = "ok"
        self.state = "stopped"
        self.inputs = KitchenMinderInputs()
        self.inputs.setupSwitch(self.switchPressed)
        self.inputs.setupPIR(self.movementDetected)
        self.apps = Set()
        CbAdaptor.__init__(self, argv)

    def switchPressed(self, channel):
        reactor.callFromThread(self.sendEvent, 'button')

    def movementDetected(self, channel):
        reactor.callFromThread(self.sendEvent, 'movement')

    def setState(self, state):
        self.state = state
        logging.debug("%s %s state = %s", ModuleName, self.id, self.state)
        msg = {"id": self.id,
               "status": "state",
               "state": self.state}
        self.sendManagerMessage(msg)

    def onStop(self):
        self.inputs.cleanup()

    def sendEvent(self, e):
        msg = {"id": self.id,
                "content": "characteristic",
                "characteristic": "gpio",
                "data": e,
                "timeStamp": time.time()
        }
        [self.sendMessage(msg, app_id) for app_id in self.apps]

    def onAppInit(self, message):
        logging.debug("%s %s %s onAppInit, req = %s", ModuleName, self.id, self.friendly_name, message)
        resp = {"name": self.name,
                "id": self.id,
                "status": "ok",
                "service": [{"characteristic": "gpio"},
                        ],
                "content": "service"}
        self.sendMessage(resp, message["id"])
        self.setState("running")

    def onAppRequest(self, message):
        self.apps.add(message["id"])

    def onAppCommand(self, message):
        logging.debug("%s %s %s onAppCommand, req = %s", ModuleName, self.id, self.friendly_name, message)

    def onConfigureMessage(self, config):
        """Config is based on what apps are to be connected.
        May be called again if there is a new configuration, which
        could be because a new app has been added.
        """
        logging.debug("%s onConfigureMessage, config: %s", ModuleName, config)
        self.setState("starting")

if __name__ == '__main__':
    adaptor = Adaptor(sys.argv)

