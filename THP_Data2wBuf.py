
# -*- coding: utf-8 -*-
"""
Created on Fri May 26 11:29:55 2023

@author: waszee
"""
import asyncio
from bleak import BleakClient
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import matplotlib.dates as mdates
#from  MS8607_smbus import * 
from pynput import keyboard

from multiprocessing import Process,Queue,Pipe
from simple_fileread_dataPlot import dread



 # address for ESP32C3_MS8670 server 1          
address = "F4:12:FA:0D:62:0A"
# service uuid="9d574107-bf90-4d24-9bb4-06d6b1e5a391"
UUID_Tc1 = "0e3149af-35f0-49a9-8262-28100c83af6a"
UUID_H1 = "6d217bea-72d8-4eb7-802d-e86fcc104d48"
UUID_P1 = "674bb9b1-e28d-4598-92b3-8669cd47b12a" 

# Another esp32 with ms8607 sensor 2
address2 = "F4:12:FA:0D:99:F2" 
#2nd server SERVICE_UUID "49a74e57-2561-49b0-97ce-08e028a77432"
UUID_Tc2 = "821ff5c6-b8aa-4dbe-98f1-0c1d735f45a0"
UUID_H2 = "7d545e25-27c2-4c10-9a36-8e0a59772bee"
UUID_P2 = "ecc244d8-b767-4131-926c-82c030e168db"
stop = 0





async def say_after(adelay, what):
    await asyncio.sleep(adelay)
    print(what)

async def get_THP1():
    client = BleakClient(address)
    print(client)
    try:
        await client.connect()
        TempC = await client.read_gatt_char(UUID_Tc1)
        humidity = await client.read_gatt_char(UUID_H1)
        pressure = await client.read_gatt_char(UUID_P1)
        encoding='utf-8'
        tc = TempC.decode(encoding)
        tout=float(tc)
        h=humidity.decode(encoding)
        hout=float(h)
        p = pressure.decode(encoding)
        pout=float(p)
        print("First Sensor")
        print("%.1f degC"%tout)
        print("%.1f percent RH"%hout)
        print("%.1f mbars"%pout)
        await client.disconnect()
        return(tout,hout,pout)
    except Exception as e:
        print(e)

async def get_THP2():
    
    #async with BleakClient("XX:XX:XX:XX:XX:XX") as client:
    client = BleakClient(address2)
    try:
        await client.connect()
        TempC = await client.read_gatt_char(UUID_Tc2)
        humidity = await client.read_gatt_char(UUID_H2)
        pressure = await client.read_gatt_char(UUID_P2)
        encoding='utf-8'
        tc = TempC.decode(encoding)
        tin=float(tc)
        h=humidity.decode(encoding)
        hin=float(h)
        p = pressure.decode(encoding)
        pin=float(p) + 1.7
        print("2nd Sensor")
        print("%.1f degC"%tin)
        print("%.1f percent RH"%hin)
        print("%.1f mbars"%pin)
        await client.disconnect()
        return(tin,hin,pin)
    except Exception as e:
        print(e)        
    
def plot(tvo,hvo,pvo,tvn,hvn,pvn,xtimes):
    fig, axs = plt.subplots(3,1,sharex=True)
    locator = mdates.AutoDateLocator()
    formatter= mdates.ConciseDateFormatter(locator)                                                                                                                              
    axs[2].xaxis.set_major_locator(locator)
    axs[2].xaxis.set_major_formatter(formatter)
    axs[0].plot(xtimes,tvo,color='blue',lw=2)
    axs[0].plot(xtimes,tvn,color='green',lw=2)
    axs[1].plot(xtimes,hvo,color='blue',lw=2)
    axs[1].plot(xtimes,hvn,color='green',lw=2)
    axs[2].plot(xtimes,pvo,color='blue',lw=2)
    axs[2].plot(xtimes,pvn,color='green',lw=2)
    #axs[2].set_ylim(1000,1020)
    axs[0].set_ylabel("TempC");
    axs[1].set_ylabel("% RH")
    axs[2].set_ylabel("hPa")
    axs[2].set_xlabel("DateTime")
    #fig.canvas.draw()
    #fig.canvas.flush_events()
    #await asyncio.sleep(1)
    
    
async def iterations(loops):
    for i in range(loops):
        yield i
        await asyncio.sleep(0.2)
        
def press_callback(key):
    if (key==keyboard.Key.esc):
        def stop_loop():
            global stop
            stop = 1
            return stop
        stop = stop_loop()
    else: stop = 0
    return stop

async def main():
    logging=False
    xdate=dt.datetime.now()
    xt= mdates.date2num(xdate)
    buffername="wBuf.txt"
    firstbufln=(f"{xt},25,25,50,50,1013,1013\n")
    with open(buffername,'w',newline='') as fbuf:
        fbuf.write(firstbufln)
    slogging=input("logging? (y/n): ") or "n"
    if(slogging =="y"): logging=True
    try:
        ipause=int(input("Time between measurements(seconds): "))
    except ValueError:
        ipause=3
    try:    
        iloops=int(input("Total number of measurements? : "))
    except ValueError:
        iloops=10
          
    l=keyboard.Listener(on_press=press_callback)
    l.start()
   
        
    # creates  a csv file and enters column lablels
    if(logging):
        dstr=dt.datetime.now().strftime("%y%m%d-%H%M%S")
        filename=f"THP_{dstr}.csv"
        fields = "adatetime,TempC_o,TempC_n, RH_o,RH_in,mbars_o,mbars_in\n"
        print(filename)
        with open(filename,'w',newline='') as f:
                f.write(fields)
    
                    
    outvalues=[25,50,1013]
    tout,hout,pout=outvalues
    invalues=[25,50,1013]
    tin,hin,pin=invalues
    
    tvo=[]
    hvo=[]
    pvo=[]
    tvn=[]
    hvn=[]
    pvn=[]
    xtimes=[]

    parent_conn,child_conn = Pipe()
    p = Process(target=dread, args=(child_conn,))
    p.start()
    
    async for i in iterations(iloops):
        # get outside readings
        try:
            print(i)
            outvalues=await get_THP1()
            print(outvalues)
            if(outvalues):tout,hout,pout=outvalues
        except Exception as e:
            tout=tout
            hout=hout
            pout=pout
            print("outside reading failed -using previous values")
            print(e)
        dtime=dt.datetime.now()
        xtimes=np.append(mdates.date2num(dtime),xtimes)
        tvo=np.append(tout,tvo)
        hvo=np.append(hout,hvo)
        pvo=np.append(pout,pvo)
        # get inside readings
        try:
            #(tin,hin,pin)=get_THP_from_MS8607()
            invalues=await get_THP2()
            if(invalues):
                tin,hin,pin = invalues
        except Exception as e:
            tin=tin
            hin=hin
            pin=pin
            print("inside readings failed -using previous values")
            print(e)
            
        #pin=pin+13.25 #correct to approx sea level value comparable to noaa values
        tvn=np.append(tin,tvn)
        hvn=np.append(hin,hvn)
        pvn=np.append(pin,pvn)
        
        xtime=mdates.date2num(dtime)
        #newline="\n"
        strdata=(f"{xtime},{tout:6.1f},{tin:6.1f},{hout:6.1f},{hin:6.1f},{pout:9.2f},{pin:9.2f}")
        #with open(buffername,'a+') as fbuf:
        #    fbuf.write(strdata)
        
        # send the data to the child process in the other module

        parent_conn.send(strdata)  # send data as string msg


        if(logging):
            strdtime=dtime
            newline="\n"
            strdata=(f"{strdtime},{tout:6.1f},{tin:6.1f},{hout:6.1f},{hin:6.1f},{pout:9.2f},{pin:9.2f}{newline}")
            with open(filename,'a+') as f:
                f.write(strdata)
            
        if stop==1:
            break
        ipstr="waited %i seconds "% (ipause)
        await say_after(ipause,ipstr)
        
    print("Stopped Collecting Data")
    p.close
    plot(tvo,hvo,pvo,tvn,hvn,pvn,xtimes)
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())
     
