
# -*- coding: utf-8 -*-
"""
Created on Fri May 26 11:29:55 2023

@author: waszee
"""
import asyncio
from bleak import BleakClient
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import matplotlib.dates as mdates
#from  MS8607_smbus import * 
import csv

address1 = "F4:12:FA:0D:62:0A" # address for this ESP32C3_MS8670 server
UUID_Tc1 = "31bc8d74-3c7c-445e-9167-0be0d082d6ac"
UUID_H1 = "b59d1151-54e8-4609-b28f-71aec7e7b647"
UUID_P1 = "0b57b9b2-8a0e-4de6-ac2b-153f5846b58b" 


address2 = "F4:12:FA:0D:99:F2" # Another esp32 with ms8607 sensor
#2nd server SERVICE_UUID "4cd0c3b5-ace1-46c8-92bc-ec930cc210ae"
UUID_Tc2 = "5eaac482-b210-4216-a269-aa20c74856b6"
UUID_H2 = "0c74216d-03be-4ccb-b29e-efc6d0ae8c54"
UUID_P2 = "e0503252-db3a-4700-884a-97e7effc2ab9"

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def get_THP1(address1):
    client = BleakClient(address1)
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

async def get_THP2(address2):
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
        pin=float(p)
        print("2nd Sensor")
        print("%.1f degC"%tin)
        print("%.1f percent RH"%hin)
        print("%.1f mbars"%pin)
        await client.disconnect()
        return(tin,hin,pin)
    except Exception as e:
        print(e)        
"""        
def createfig(ipause,iloops):
    fig,axs=plt.subplots(3,1,sharex=True)
    xt1=dt.datetime.now()
    xt2=xt1+dt.timedelta(seconds=ipause*iloops)
    start=mdates.date2num(xt1)
    stop=mdates.date2num(xt2)
    axs[2].set_xlim(start,stop)
    fig.canvas.draw()
    fig.show()
 """
    
def plot(axs,tvo,hvo,pvo,tvn,hvn,pvn,xtimes):
    #fig,axs=plt.subplots(3,1,sharex=True)
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
    
    axs[2].set_ylim(1000,1020)
    axs[0].set_ylabel("TempC");
    axs[1].set_ylabel("% RH")
    axs[2].set_ylabel("hPa")
    axs[2].set_xlabel("DateTime")

async def iterations(loops):
    for i in range(loops):
        yield i
        await asyncio.sleep(0.5)

async def main(address1,address2):
    logging=False
    filename="none"
    ipause=10
    iloops=30
    
    # creates  a csv file and enters column lablels
    if(logging):
        dstr=dt.datetime.now().strftime("%y%m%d-%H%M%S")
        filename=f"THP_{dstr}.csv"
        fields = ['adatetime','mbars_o','RH%_o','TempC_o','mbars_in','RH%_in','TempC_in']
        print(filename)
        with open(filename,'w',newline='') as file:
                writer=csv.writer(file)
                writer.writerow(fields)
    plt.ion()
    outvalues=[25,50,1013]
    tout,hout,pout=outvalues
    invalues=[20,45,1013]
    tin,hin,pin=invalues
    #createfig(ipause,iloops)
    fig,axs=plt.subplots(3,1,sharex=True)
   
    tvo=[]
    hvo=[]
    pvo=[]
    tvn=[]
    hvn=[]
    pvn=[]
    xtimes=[]
    
    async for i in iterations(iloops):
        try:
            outvalues=await get_THP1(address1)
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
        try:
            #(tin,hin,pin)=get_THP_from_MS8607()
            invalues=await get_THP2(address2)
            if(invalues):tin,hin,pin = invalues                
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
        plot(axs,tvo,hvo,pvo,tvn,hvn,pvn,xtimes)
        fig.canvas.draw()
        fig.canvas.flush_events()
        if(logging):
            with open(filename,'w',newline='') as file:
                writer=csv.writer(file)
                writer.writerow([dtime.strftime,pvo,hvo,tvo,pvn,hvn,tvn])
            
        print(i*ipause)
        ipstr="waited %i seconds "% (ipause)
        await say_after(ipause,ipstr)

if __name__ == "__main__":
    asyncio.run(main(address1,address2))
     
