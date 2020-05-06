from pywizlight.pywizlight.bulb import wizlight, PilotBuilder
import asyncio
import asyncio_dgram
import sys


# create/get the current thread's asyncio loop
loop = asyncio.get_event_loop()

bulbIp = "192.168.1.240"
bulbPort = 38899
macAddress = "a8bb508bf008"
timeout = 60
# setup a standard light
'''
light = wizlight(bulbIp)
# setup the light with a custom port
# light = wizlight(bulbIp)

state = asyncio.run(asyncio.wait_for(light.updateState(), 60))
print(state.get_state())
print(state.get_brightness())

r, g, b = state.get_rgb()
print("{}, {}, {}".format(r, g, b))
'''


async def recData(stream):
    data, address = await asyncio.wait_for(stream.recv(), timeout)
    return data


async def sendCommand(message):
    message = r'{"method":' + message + r',"params":{}}'
    maxTries = 100
    sleepInterval = 0.5
    dataStream = await asyncio.wait_for(asyncio_dgram.connect((bulbIp, bulbPort)), timeout)

    receive = asyncio.create_task(recData(dataStream))

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


print("Sending command...")
resp = asyncio.run(asyncio.wait_for(sendCommand(r'"getPilot"'), 60))
print(resp)


