from plugp100.api.tapo_client import TapoClient, AuthCredential
from plugp100.api.light_device import LightDevice
import asyncio
import time

async def main():
    credential = AuthCredential("adrianje77@gmail.com", "testing123")
    client1 = await TapoClient.connect(credential, "192.168.1.47")
    light1 = LightDevice(client1)
    client2 = await TapoClient.connect(credential, "192.168.1.48")
    light2 = LightDevice(client2)

    await light1.set_brightness(1)
    await light2.set_brightness(1)
    await light1.set_color_temperature(2500)
    await light2.set_color_temperature(2500)
    
    for i in range(100):
        await asyncio.gather(light1.set_brightness((i+1)), light2.set_brightness((i+1)))
        #await asyncio.sleep(0.05) 
        print(i)
        
        #await light1.set_hue_saturation(hue=((i+1)*45)//100, saturation=100-i)
        #await light2.set_hue_saturation(hue=((i+1)*45)//100, saturation=100-i)
        
        #await light1.set_color_temperature(2500+10*i)
        #await light2.set_color_temperature(2500+10*i)
        
        #await light1.set_hue_saturation(hue=100, saturation=100)
        #await light2.set_hue_saturation(hue=100, saturation=100)

        #await light1.set_color_temperature(2500)
        #await light2.set_color_temperature(2500)
        
    await client1.close()
    await client2.close()

asyncio.run(main())