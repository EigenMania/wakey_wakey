from plugp100.api.tapo_client import TapoClient, AuthCredential
from plugp100.api.light_device import LightDevice
import asyncio
import os

SUNRISE_DURATION_MIN = 30 # How long the sunrise should last in minutes

async def get_clients():
    username = os.getenv("WAKEY_USERNAME") # "adrianje77@gmail.com"
    password = os.getenv("WAKEY_PASSWORD") # "testing123"
    iplist_string = os.getenv("WAKEY_IPLIST") # "192.168.1.47|192.168.1.48"
    if any( [x==None for x in [username,password,iplist_string]] ):
        raise("One of WAKEY_USERNAME, WAKEY_PASSWORD, WAKEY_IPLIST environment variables undefined.")
    credential = AuthCredential(username, password)
    iplist = iplist_string.split("|")

    # TODO (p-casgrain): Pythonify into nice list comprehension, clients are now created without the "connect" function, but need to be initialized afterwards.
    clients = []
    for ip in iplist:
        clients.append(TapoClient(credential,ip))

    for client in clients:
        await client.initialize()

    # Not working anymore after commit 1923265 from plugp100 library
    #clients = await asyncio.gather(*[TapoClient.connect(credential,x) for x in iplist])
    return clients

async def main():
    clients = await get_clients()
    lights = [LightDevice(x) for x in clients]

    # First reduce brightness and then set sunrise temperature.
    await asyncio.gather(*[x.set_brightness(1) for x in lights])
    #await asyncio.gather(*[x.set_color_temperature(2500) for x in lights])
    await asyncio.gather(*[x.set_hue_saturation(hue=0, saturation=100) for x in lights])

    dt = SUNRISE_DURATION_MIN*60//100 # Loop pause time in seconds
    
    for i in range(100):
        cur_brightness = i+1
        cur_hue = int((i+1)*50/100)
        cur_saturation = 100-int(0.7*i)
        # For debugging...
        #print("Brightness: ", cur_brightness)
        #print("Hue       : ", cur_hue)
        #print("Saturation: ", cur_saturation)
        #print("")
        await asyncio.gather(*[x.set_brightness(cur_brightness) for x in lights])
        #await asyncio.gather(*[x.set_color_temperature(2500+i) for x in lights])
        await asyncio.gather(*[x.set_hue_saturation(hue=cur_hue, saturation=cur_saturation) for x in lights])
        await asyncio.sleep(dt)

    await asyncio.gather(*[x.close() for x in clients])


if __name__=='__main__':
    asyncio.run(main())
