import asyncio
import asyncio_dgram
import sys
import time

from controlFunctions import WizBulb
from moodDetect import MoodDetect

async def main():
    bulbIp = "192.168.1.240"
    bulbPort = 38899
    listenPort = 38900
    macAddress = "a8bb508bf008"
    timeout = 60

    light = WizBulb(bulbIp, listenPort, bulbPort, macAddress)
    mood = MoodDetect()

    mood.startStream()

    print("Sending command...")
    resp = await light.getStatus()
    print(resp)
    config = await light.getConfig()
    print(config)

    currentRgb = {"r": 255, "g": 0, "b": 255}
    speed = 10

    try:
        onStatus = await light.isOn()
        if not onStatus:
            await light.turnOn()
        await light.clearSettings()

        lastVal = None
        lastRms = 0
        diff = 2
        noneCount = 0
        noneFlag = False
        while True:
            val = mood.averageOfAverage()
            if val:
                noneCount = 0
                noneFlag = False
                if lastVal:
                    diff = mood.calcCentDifference(lastVal, val)
                lastVal = val
            else:
                noneCount += 1
                if noneCount == 5:
                    diff = None
                    currentRgb = {"r": 0, "g": 0, "b": 255}
                    noneCount = 5
                    noneFlag = True
            print(currentRgb)
            currentRgb = await light.rgbChange(diff, currentRgb, 10, noneFlag)

    except KeyboardInterrupt:
        time.sleep(2)
        await light.turnOff()
    
    finally:
        time.sleep(2)
        await light.turnOff()

if __name__ == "__main__":
    asyncio.run(main())


