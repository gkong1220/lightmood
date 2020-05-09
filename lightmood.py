import asyncio
import asyncio_dgram
import sys
import time

from controlFunctions import WizBulb

async def main():
    bulbIp = "192.168.1.240"
    bulbPort = 38899
    listenPort = 38900
    macAddress = "a8bb508bf008"
    timeout = 60

    light = WizBulb(bulbIp, listenPort, bulbPort, macAddress)

    print("Sending command...")
    resp = await light.getStatus()
    print(resp)
    print(type(resp))
    config = await light.getConfig()
    print(config)

    onStatus = await light.isOn()
    if not onStatus:
        await light.turnOn()
    
    print(await light.clearSettings())
    print(await light.getStatus())

    await light.setSpeed(10)
    '''
    await light.setRgb(light.getRgb("red"))
    print("red")
    await light.setRgb(light.getRgb("green"))
    print("green")
    await light.setRgb(light.getRgb("blue"))
    print("blue")
    await light.setRgb(light.getRgb("jesus"))
    '''
    await light.redToBlue()
    print(await light.getStatus())
    await light.setRgb(light.getRgb("jesus"))
    await light.turnOff()
    # asyncio.run(light.turnOff())
    # asyncio.run(asyncio.sleep(3))
    # asyncio.run(light.turnOn())


if __name__ == "__main__":
    asyncio.run(main())


