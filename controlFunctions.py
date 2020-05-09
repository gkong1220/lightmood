import asyncio
import asyncio_dgram
import sys
import json
import time

class WizBulb(object):

    def __init__(self, bulbIp, listenerPort, bulbPort, bulbMac):
        self.bulbIp = bulbIp
        self.listenerPort = listenerPort
        self.bulbPort = bulbPort
        self.bulbMac = bulbMac
        self.timeout = 60
        self.infoStream = None
        self.lightOn = False
        self.currRgb = None
        self.speed = 100


    #---------------Transitional Themes---------------#
    async def redToBlue(self):
        currRgb = self.getRgb("red")
        while currRgb["g"] < 256:
            currRgb["r"] -= self.speed
            currRgb["g"] += self.speed
            await self.setRgb(currRgb)

    #---------------Get Functions---------------#
    def getRgb(self, color):
        colors = {"grape":      {"r": 82,   "g": 65,    "b": 76},
                    "pea":      {"r": 91,   "g": 140,   "b": 90},
                    "fire":     {"r": 227,  "g": 101,   "b": 91},
                    "jesus":    {"r": 252,  "g": 250,   "b": 164},
                    "red":      {"r": 255,  "g": 0,     "b": 0},
                    "blue":     {"r": 0,    "g": 0,   "b": 255}, 
                    "green":    {"r": 0,    "g": 255,     "b": 0}
                    }
        if color == "list":
            return colors.keys()
        else:
            return colors[color]


    def getCurrentRgb(self):
        return self.currRgb


    async def getStatus(self):
        status = json.loads(await self.sendCommand(r'{"method":"getPilot","params":{}}'))
        self.lightOn = status["result"]["state"]
        return status


    async def getConfig(self):
        return await self.sendCommand(r'{"method":"getSystemConfig","params":{}}')

    #---------------Set Functions---------------#
    async def clearSettings(self):
        return await self.sendCommand(r'{"method":"setPilot","params":{"sceneId": 0}}')


    async def turnOn(self):
        if self.lightOn:
            print("Light already on.")
            return
        self.lightOn = True
        return await self.sendCommand(r'{"method":"setPilot","params":{"state":true}}')

    async def turnOff(self):
        if not self.lightOn:
            print("Light already off.")
            return
        return await self.sendCommand(r'{"method":"setPilot","params":{"state":false}}')

    async def setRgb(self, rgb):
        if self.lightOn:
            self.currRgb = rgb
            if self.speed:
                rgb["speed"] = self.speed
            command = json.dumps({"method": "setPilot", "params": rgb})
            return await self.sendCommand(command)
        else:
            print("Light not on...no rgb set.")

    async def setSpeed(self, speed):
        self.speed = speed
        command = json.dumps(
            {"method": "setPilot", "params": {"speed": speed}})
        return await self.sendCommand(command)


    async def register(self):
        return await self.sendCommand(r'{"method": "registration", "id": 1, "params": {"phoneIp": "192.168.86.20", "register": true, "homeId": 410989, "phoneMac": "ec2ce214ce2b"}}')

    
    async def infoListener(self):
        print("Listening for info...")
        self.infoStream = await asyncio.wait_for(asyncio_dgram.connect((self.bulbIp, self.listenerPort)), self.timeout)

        infoData = asyncio.create_task(self.recData(self.infoStream))

        await infoData

        resInfoData = infoData.result()
        self.infoStream.close

        if resInfoData and len(resInfoData):
            return resInfoData.decode()


    async def listenInfoStream(self):
        if self.infoStream:
            infoData = asyncio.create_task(self.recData(self.infoStream))
            await infoData
            resInfoData = infoData.result()
            self.infoStream.close
            if resInfoData and len(resInfoData):
                return resInfoData.decode()
        else:
            print("ERROR: no info stream detected.")


    def closeListenerStream(self):
        self.infoStream.close
        print("Stream Closed.")


    async def isOn(self):
        status = await self.getStatus()
        self.lightOn = status["result"]["state"]
        return self.lightOn


    async def recData(self, stream):
        data, address = await asyncio.wait_for(stream.recv(), self.timeout)
        return data


    async def sendCommand(self, message):
        # message = r'{"method":' + message + r',"params":{}}'
        maxTries = 100
        sleepInterval = 0.5
        dataStream = await asyncio.wait_for(asyncio_dgram.connect((self.bulbIp, self.bulbPort)), self.timeout)

        receive = asyncio.create_task(self.recData(dataStream))

        i = 0
        while not receive.done() and i < maxTries:
            asyncio.create_task(dataStream.send(bytes(message, "utf-8")))
            await asyncio.sleep(0.5)
            i += 1

        await receive
        resData = receive.result()

        dataStream.close

        if resData and len(resData):
            return resData.decode()
