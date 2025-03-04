# Original repository: https://github.com/petretiandrea/plugp100
# To update: pip install plugp100 --upgrade
import asyncio
from plugp100.common.credentials import AuthCredential
from plugp100.new.device_factory import connect, DeviceConnectConfiguration
import os
import sys

n = len(sys.argv)
SUNRISE_DURATION_MIN = 30
# For command line testing, pass in shorter sunrise durations when calling wakey_wakey.pi
if n == 2:
    SUNRISE_DURATION_MIN = int(sys.argv[1])

async def get_devices():
    """Get and initialize a list of Tapo devices based on IP"""
    username = os.getenv("WAKEY_USERNAME") # Your Tapo email
    password = os.getenv("WAKEY_PASSWORD") # Your Tapo password
    iplist_string = os.getenv("WAKEY_IPLIST") # Your Tapo L530 IP addresses, e.g. "192.168.1.47|192.168.1.48"
    
    if any( [x==None for x in [username,password,iplist_string]] ):
        raise("One of WAKEY_USERNAME, WAKEY_PASSWORD, WAKEY_IPLIST environment variables undefined.")
    credentials = AuthCredential(username, password)
    
    iplist = iplist_string.split("|")
    
    devices = []
    for ip in iplist:
        device_configuration = DeviceConnectConfiguration(
            host=ip,
            credentials=credentials
        )
        device = await connect(device_configuration)
        await device.update()
        devices.append(device)

    return devices

async def sunrise_step(light, brightness, hue, saturation):
    """Modify the brightness, hue, and saturation for a single device"""
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
    lights = []
    while not lights_initialized and attempts < 10:
        print("Current connection attempt: {}".format(attempts))
        try:
            lights = await get_devices()
            # Sunrise begins with lowest brightness red color
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

    print("Sunrise finished! Closing light client connections...")
    await asyncio.gather(*[light.client.close() for light in lights])
    
    return

if __name__=='__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.run_until_complete(asyncio.sleep(0.1))
    loop.close()
