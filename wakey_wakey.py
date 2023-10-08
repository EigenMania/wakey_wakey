from plugp100.api.tapo_client import TapoClient, AuthCredential
from plugp100.api.light_device import LightDevice
import asyncio
import os

async def get_clients():
    username = os.getenv("WAKEY_USERNAME") # "adrianje77@gmail.com"
    password = os.getenv("WAKEY_PASSWORD") # "testing123"
    iplist_string = os.getenv("WAKEY_IPLIST") # "192.168.1.47|192.168.1.48"
    if any( [x==None for x in [username,password,iplist_string]] ):
        raise("One of WAKEY_USERNAME, WAKEY_PASSWORD, WAKEY_IPLIST environment variables undefined.")
    credential = AuthCredential(username, password)
    iplist = iplist_string.split("|")
    clients = await asyncio.gather(*[TapoClient.connect(credential,x) for x in iplist])
    return clients


async def main():
    clients = await get_clients()
    lights = [LightDevice(x) for x in clients]

    await asyncio.gather(*[x.off() for x in lights])
    await asyncio.gather(*[x.set_color_temperature(2500) for x in lights])
    
    for i in range(100):
        await asyncio.gather(*[x.set_brightness(i+1) for x in lights])
        # await asyncio.gather(*[x.set_hue_saturation(hue=((i+1)*45)//100, saturation=100-i) for x in lights])
        # await asyncio.gather(*[x.t_color_temperature(2500+10*i) for x in lights])
        await asyncio.sleep(0.05)         
        
    await asyncio.gather(*[x.close() for x in clients])


if __name__=='__main__':
    asyncio.run(main())