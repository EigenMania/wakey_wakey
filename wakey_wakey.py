# Original repository: https://github.com/petretiandrea/plugp100
# To update: pip install plugp100 --upgrade
from plugp100.api.tapo_client import TapoClient, AuthCredential
from plugp100.api.light_device import LightDevice
import asyncio
import os
import sys

n = len(sys.argv)
SUNRISE_DURATION_MIN = 30
if n == 2:
    SUNRISE_DURATION_MIN = int(sys.argv[1])

async def get_clients():
    username = os.getenv("WAKEY_USERNAME") # Your Tapo email
    password = os.getenv("WAKEY_PASSWORD") # Your Tapo password
    iplist_string = os.getenv("WAKEY_IPLIST") # Your Tapo L530 IP addresses, e.g. "192.168.1.47|192.168.1.48"
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

    return clients

async def sunrise_step(light, brightness, hue, saturation):
    sunrise_step_succeeded = False
    try:
        await light.set_brightness(brightness)
        await light.set_hue_saturation(hue=hue, saturation=saturation)
        sunrise_step_succeeded = True
    except:
        sunrise_step_succeeded = False
    
    return sunrise_step_succeeded

async def main():
    attempts = 0
    lights_initialized = False
    while not lights_initialized and attempts < 10:
        print("Current connection attempt: {}".format(attempts))
        try:
            clients = await get_clients()
            lights = [LightDevice(x) for x in clients]
            # First reduce brightness and then set sunrise temperature.
            #await asyncio.gather(*[x.set_brightness(1) for x in lights])
            #await asyncio.gather(*[x.set_color_temperature(2500) for x in lights])
            #await asyncio.gather(*[x.set_hue_saturation(hue=0, saturation=100) for x in lights])
            await asyncio.gather(*[sunrise_step(x, 1, 0, 100) for x in lights])
            lights_initialized = True
        except:
            asyncio.sleep(5)
            attempts = attempts + 1
            lights_initialized = False

    if (lights_initialized):
        print("Lights initialized successfully!\n")
    else:
        print("Lights failed to initialize... :(\n")
        
    dt = SUNRISE_DURATION_MIN*60//100 # Loop pause time in seconds
    
    for i in range(100):
        cur_brightness = i + 1
        cur_hue = int((i + 1)*50/100)
        cur_saturation = 100 - int(0.90*i)
        #cur_brightness = 50
        #cur_hue = 345
        #cur_saturation = 100
        
        # For debugging...
        print("Sunrise Step #{}".format(i))
        print("Brightness: ", cur_brightness)
        print("Hue       : ", cur_hue)
        print("Saturation: ", cur_saturation)
        print("")

        attempts = 0
        lights_changed = False
        while not lights_changed and attempts < 10:
            print("Current attempt {} to change lights...\n".format(attempts))
            try:
                # Perform the sunrise step
                await asyncio.gather(*[sunrise_step(x, cur_brightness, cur_hue, cur_saturation) for x in lights])
                #await asyncio.gather(*[x.set_brightness(cur_brightness) for x in lights])
                #await asyncio.gather(*[x.set_color_temperature(2500+i) for x in lights])
                #await asyncio.gather(*[x.set_hue_saturation(hue=cur_hue, saturation=cur_saturation) for x in lights])
                lights_changed = True
            except:
                asyncio.sleep(5)
                attempts = attempts + 1
                lights_changed = False

        if (lights_changed):
            print("Lights successfully changed!\n")
        else:
            print("Failed to change lights... :(\n")

        await asyncio.sleep(dt)

    await asyncio.gather(*[x.close() for x in clients])


if __name__=='__main__':
    asyncio.run(main())
