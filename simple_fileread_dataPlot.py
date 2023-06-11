
from math import e
import webbrowser
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from multiprocessing import Process,Queue,Pipe
from matplotlib.animation import FuncAnimation
 

def dread(child_conn):
    
    def update():
        xtimes=data[:,0]
        tvo=data[:,1]
        tvn=data[:,2]
        hvo=data[:,3]
        hvn=data[:,4]
        pvo=data[:,5]
        pvn=data[:,6]
        plot(tvo,hvo,pvo,tvn,hvn,pvn,xtimes)
    

    def plot(tvo,hvo,pvo,tvn,hvn,pvn,xtimes):
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
        axs[0].set_ylabel("TempC")
        axs[1].set_ylabel("% RH")
        axs[2].set_ylabel("hPa")
        axs[2].set_xlabel("DateTime")
        fig.canvas.draw_idle()
        fig.canvas.flush_events()


    plt.ion()
    fig, axs = plt.subplots(3,1,sharex=True)
    data=[]
    while True:
        print(np.size(data))
        try:
            rtext=child_conn.recv()
        except Exception as e:
            print(e)
            break
                    
        values = [float(i) for i in rtext.split(',')]
        newrow=np.array([values])
        if (np.size(data)<7): data=newrow
        else:
            data=np.vstack([data, newrow])
        
        update()
        plt.show()
     
    child_conn.close()

