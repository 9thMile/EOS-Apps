#! /usr/bin/env python
import sys
import socket
import fcntl
import struct
#import netifaces
import urllib2
import subprocess
from time import sleep
from datetime import date, datetime, time, timedelta, tzinfo
import eossql as eoss
import eosutils as eosu
import eospull as eosp
import MySQLdb as mdb
import Tkinter as tk
import ttk
import tkFont as tkf
from PIL import Image
from PIL import ImageTk
import StringIO as cS
import urllib, cStringIO
import webbrowser

global stations
global stationId
global StationIndex


def dotable(*args):
    try:
        a = tableval.get()
        ##'Alarm','Almanac','Archive','Date','Depth','Feed','Pressure','Rain','Relay','Soil','Solar','Temp','Wind'
        if a == 'Temp':
            URL = "http://" + server.get() + "/tables/temp_table.php"
        elif a == 'Board':
            URL = "http://" + server.get() + "/tables/board_table.php"          
        elif a == 'Alarm':
            URL = "http://" + server.get() + "/tables/alarm_table.php"
        elif a == 'Almanac':
            URL = "http://" + server.get() + "/tables/almanac_table.php"
        elif a == 'Archive':
            URL = "http://" + server.get() + "/tables/archive_table.php"
        elif a == 'Date':
            URL = "http://" + server.get() + "/tables/coredate_table.php"
        elif a == 'Depth':
            URL = "http://" + server.get() + "/tables/depth_table.php"
        elif a == 'Feed':
            URL = "http://" + server.get() + "/tables/feed_table.php"
        elif a == 'Pressure':
            URL = "http://" + server.get() + "/tables/pressure_table.php"
        elif a == 'Rain':
            URL = "http://" + server.get() + "/tables/rain_table.php"
        elif a == 'Relay':
            URL = "http://" + server.get() + "/tables/relay_table.php"
        elif a == 'Soil':
            URL = "http://" + server.get() + "/tables/soil_table.php"
        elif a == 'Solar':
            URL = "http://" + server.get() + "/tables/solar_table.php"
        elif a == 'Wind':
            URL = "http://" + server.get() + "/tables/wind_table.php"
        else:
            URL = ''
        if URL <> '':
            webbrowser.open(URL)
        
    except:
        pass

def donoaareport(*args):
    global StationIndex
    try:
        
        noaaReport = ttk.Labelframe(tab4, text=  reportval.get(), style="BM.TLabelframe")
        noaaReport.grid(column=0, row=2, sticky=("N"))
        scrollStyle = ttk.Style()
        scrollStyle.configure("BM.Vertical.TScrollbar", foreground="black", background="white", width= 20)
        
        
        if reportval.get() == 'NOAA Month':
            URL = "http://www.eosweather.ca/burst/" + StationIndex + "/noaamo.txt"
        elif reportval.get() == 'NOAA Year':
            URL = "http://www.eosweather.ca/burst/" + StationIndex + "/noaayr.txt"
        elif reportval.get() == 'NOAA Previous Year':
            URL = "http://www.eosweather.ca/burst/" + StationIndex + "/noaapryr.txt"
        elif reportval.get() == 'NOAA Previous Month':
            URL = "http://www.eosweather.ca/burst/" + StationIndex + "/noaaprmo.txt"
        else:
            URL = ''
        u = urllib.urlopen(URL)
        raw_data = u.read()
        sbar = ttk.Scrollbar(noaaReport)
        sbar.grid(column=2,row=0, sticky="N, S, E, W")
        
        sbar['style'] = "BM.Vertical.TScrollbar"
        noaatext = tk.Text(noaaReport, height=20, width=85, yscrollcommand=sbar.set)
       
        noaatext.grid(column=1, row=0)
        sbar.config(command=noaatext.yview)
        noaatext.insert("1.0", raw_data)
    
        
    except:
        pass

def dosummary(*args):
    global StationIndex

    try:

        try:
            WindSpeed, WindHi, BarMax, BarMin, TempMin, TempMax, WindRun, Rain = eosp.getsummary(StationIndex,1)
            d_lowTemp.set("{0:.1f} C ".format(float(TempMin)))
            d_hiTemp.set("{0:.1f} C ".format(float(TempMax)))
            d_lowPress.set("{0:.1f} kPa ".format(float(BarMin) / 10))
            d_hiPress.set("{0:.1f} kPa ".format(float(BarMax) / 10))
            d_avgWind.set("{0:.1f} km/h ".format(float(WindSpeed)))
            d_hiWind.set("{0:.1f} km/h ".format(float(WindHi)))
            d_runWind.set("{0:.1f} km ".format(float(WindRun)))
            r_1days.set("{0:.1f} mm".format(float(Rain)))

            WindSpeed7, WindHi7, BarMax7, BarMin7, TempMin7, TempMax7, WindRun7, Rain7 = eosp.getsummary(StationIndex,7)

            w_lowTemp.set("{0:.1f} C ".format(float(TempMin7)))
            w_hiTemp.set("{0:.1f} C ".format(float(TempMax7)))
            w_lowPress.set("{0:.1f} kPa ".format(float(BarMin7) / 10))
            w_hiPress.set("{0:.1f} kPa ".format(float(BarMax7) / 10))
            w_avgWind.set("{0:.1f} km/h ".format(float(WindSpeed7)))
            w_hiWind.set("{0:.1f} km/h ".format(float(WindHi7)))
            r_7days.set("{0:.1f} mm".format(float(Rain7)))
            
            wd_lowTemp.set(eosp.getitemdate(StationIndex,'LOWTEMP',TempMin7,"7"))
            wd_hiTemp.set(eosp.getitemdate(StationIndex,'MAXTEMP',TempMax7,"7"))
            wd_hiPress.set(eosp.getitemdate(StationIndex,'MAXBAR',BarMax7,"7"))
            wd_lowPress.set(eosp.getitemdate(StationIndex,'MINBAR',BarMin7,"7"))
            wd_hiWind.set(eosp.getitemdate(StationIndex,'HIGHWIND',WindHi7,"7"))
               
            WindSpeed30, WindHi30, BarMax30, BarMin30, TempMin30, TempMax30, WindRun30, Rain30 = eosp.getsummary(StationIndex,30)    

            m_lowTemp.set("{0:.1f} C ".format(float(TempMin30)))
            m_hiTemp.set("{0:.1f} C ".format(float(TempMax30)))
            m_lowPress.set("{0:.1f} kPa ".format(float(BarMin30)/10))
            m_hiPress.set("{0:.1f} kPa ".format(float(BarMax30)/10))
            m_avgWind.set("{0:.1f} km/h ".format(float(WindSpeed30)))
            r_30days.set("{0:.1f} mm".format(float(Rain30)))

            md_lowTemp.set(eosp.getitemdate(StationIndex,'LOWTEMP',TempMin30,"30"))
            md_hiTemp.set(eosp.getitemdate(StationIndex,'MAXTEMP',TempMax30,"30"))
            md_hiPress.set(eosp.getitemdate(StationIndex,'MAXBAR',BarMax30,"30"))
            md_lowPress.set(eosp.getitemdate(StationIndex,'MINBAR',BarMin30,"30"))
            md_hiWind.set(eosp.getitemdate(StationIndex,'HIGHWIND',WindHi30,"30"))             

            root.after(1000 * 60 * 10, dosummary)    ## 10  minutes 
        except:
            d_lowTemp.set("")
            d_lowTemp.set("")
            d_hiTemp.set("")
            d_lowPress.set("")
            d_hiPress.set("")
            d_avgWind.set("")
            d_hiWind.set("")
            d_runWind.set("")
            d_sun.set("")
            w_lowTemp.set("")
            w_hiTemp.set("")
            w_lowPress.set("")
            w_hiPress.set("")
            w_avgWind.set("")
            w_hiWind.set("")
            w_sun.set("")
            w_lowTemp.set("")
            w_hiTemp.set("")
            w_lowPress.set("")
            w_hiPress.set("")
            w_avgWind.set("")
            w_hiWind.set("")
            w_sun.set("")           
            wd_lowTemp.set("")
            wd_hiTempset("")
            wd_lowPress.set("")
            wd_hiPress.set("")
            wd_hiWind.set("")
            wd_sun.set("")
            m_lowTemp.set("")
            m_hiTemp.set("")
            m_lowPress.set("")
            m_hiPress.set("")
            m_avgWind.set("")
            m_hiWind.set("")
            m_sun.set("")
            md_lowTemp.set("")
            md_hiTemp.set("")
            md_lowPress .set("")
            md_hiPress.set("")
            md_hiWind.set("")
            md_sun.set("")
    except:
        pass
    
        
def docharts(*args):
    g = graphval.get()
    Report = ttk.Labelframe(tab3, text=g, style="BM.TLabelframe")
    Report.grid(column=0, row=1, sticky=("W, N"))     
    if g == 'Temp':
        tempphoto = getimage("temp.png")
        templabel = ttk.Label(Report, image=tempphoto)
        templabel.image = tempphoto
        templabel.grid(column=0, row=0, sticky=("W, E"))
        tempnowphoto = getimage("tempnow.png")
        tempnowlabel = ttk.Label(Report, image=tempnowphoto)
        tempnowlabel.image = tempnowphoto
        tempnowlabel.grid(column=1, row=0, sticky=("W, E"))
    elif g == 'Wind':              
        windphoto = getimage("wind.png")
        windlabel = ttk.Label(Report, image=windphoto)
        windlabel.image = windphoto
        windlabel.grid(column=0, row=0, sticky=("W, E"))    
        windnowphoto = getimage("windnow.png")
        windnowlabel = ttk.Label(Report, image=windnowphoto)
        windnowlabel.image = windnowphoto
        windnowlabel.grid(column=1, row=0, sticky=("W, E"))
    elif g == 'Solar':               
        solarphoto = getimage("solar.png")
        solarlabel = ttk.Label(Report, image=solarphoto)
        solarlabel.image = solarphoto
        solarlabel.grid(column=0, row=0, sticky=("W, E"))
        solarnowphoto = getimage("solarnow.png")
        solarnowlabel = ttk.Label(Report, image=solarnowphoto)
        solarnowlabel.image = solarnowphoto
        solarnowlabel.grid(column=1, row=0, sticky=("W, E"))
    elif g == 'Pressure':              
        pressphoto = getimage("pressure.png")
        presslabel = ttk.Label(Report, image=pressphoto)
        presslabel.image = pressphoto
        presslabel.grid(column=0, row=0, sticky=("W, E"))
        pressnowphoto = getimage("pressurenow.png")
        pressnowlabel = ttk.Label(Report, image=pressnowphoto)
        pressnowlabel.image = pressnowphoto
        pressnowlabel.grid(column=1, row=0, sticky=("W, E"))

    elif g == 'Board':
        voltphoto = getimage("bvolts.png")
        voltlabel = ttk.Label(Report, image=voltphoto)
        voltlabel.image = voltphoto
        voltlabel.grid(column=0, row=0, sticky=("W, E"))
        btempphoto = getimage("btemp.png")
        btemplabel = ttk.Label(Report, image=btempphoto)
        btemplabel.image = btempphoto
        btemplabel.grid(column=1, row=0, sticky=("W, E"))

    
def getimage(fname):
    global StationIndex
    try:
        tempimage = Image.open("/var/www/img/na.gif")
        temp = tempimage.resize((300, 300),Image.ANTIALIAS)
        img = ImageTk.PhotoImage(temp)
        URL = "http://www.eosweather.ca/burst/" + StationIndex + "/" + fname
        try:
            filelike = cStringIO.StringIO(urllib.urlopen(URL).read())
            tempimage = Image.open(filelike)
            temp = tempimage.resize((300, 300),Image.ANTIALIAS)
            img = ImageTk.PhotoImage(temp)
        except:
            pass
    except:
        pass
    return img
def geticon(fname):
    tempimage = Image.open(fname)
    temp = tempimage.resize((30, 30),Image.ANTIALIAS)
    return ImageTk.PhotoImage(temp)

def getuv(trend):
    if (trend == 0):
        return "None/N/A"
    if (trend == 1):
        return "Very Low"
    if (trend == 2):
        return "Low"
    if (trend == 3):
        return "Moderate"
    if (trend == 4):
        return "Moderate"
    if (trend == 5):
        return "Moderate"
    if (trend == 6):
        return "High"
    if (trend == 7):
        return "High"
    if (trend == 8):
        return "High"
    if (trend == 9):
        return "High"
    if (trend >= 10):
        return "Extream"

def getalarms(*args):
    global StationIndex
    try:
        listalarm.delete(0,tk.END)
        Alarms = []
        Alarms = eosp.getalarms(StationIndex,1)
        if len(Alarms) > 0:
            for row in Alarms:
                
                listalarm.insert(tk.END,row)
        else:
            listalarm.insert(tk.END,"No Alarms Active")

        root.after(1000 * 60 * 1, getalarms)    ## 10  minutes 
    except:
        pass


def getweather(*args):
    global StationIndex
    strError.set("")
    Index = stationval.get()
    x = 0
    for t in stations:
        if t == Index:
            y = x
        x = x + 1
    Id = stationId[y]
    StationIndex = Id

    try:
        strError.set(StationIndex)
        Wind, Rain, Pressure, Solar, Temp, Board, Tide, We_Date_Time = eosp.getburst(Id)
        MeanTemp, MaxTemp, LowTemp, WindPeak = eosp.getdaily(Id)
        We_Date, We_Time, TempOut, TempHi, TempLow, Wind10Avg, WindHi, RainA, Rain_Rate, SolarRadHi, SolarEnergy, Cloud = eosp.getarchive(Id)
        w_split = Wind.split('-')
        t_split = Temp.split('-')
        b_split = Board.split('-')
        p_split = Pressure.split('-')
        s_split = Solar.split('-')
        r_split = Rain.split('-')
        
        ##print "cycle"  
        version.set(str(float(b_split[10])/100 + float(b_split[9])))
        battery.set(str(float(b_split[1]) + (float(b_split[2])/10)))
        source.set(str(float(b_split[3]) + (float(b_split[4])/10)))
        btemp = float(b_split[5])
        if int(b_split[6]) == 1:
            btemp = (256 - btemp) * -1
        cabTemp.set(str(btemp))
        feedTime.set(We_Date_Time)
        archived.set(We_Date + " " + We_Time)
        spd = float(w_split[1]) + (float(w_split[2])/10)
        w_spd.set("{0:.1f} Kph".format(spd))
        wdir = float(w_split[8]) + float(w_split[9])
        if spd > 0:
            w_rose = eosu.wind.windrose(wdir)
        else:
            w_rose = '---'
        w_dir.set(w_rose)
        w_10min.set("{0:.1f} Kph".format(float(Wind10Avg)))
        w_gust.set("{0:.1f} Kph".format(float(WindHi)))
        out = round(float(t_split[1]) + (float(t_split[2])/ 10),1)
        dew = round(float(t_split[3]) + (float(t_split[4])/ 10),1)
        rel = float(t_split[5])
        if float(t_split[6]) == 1:
            out = out * -1
        if float(t_split[7]) == 1:
            dew = dew * -1
        if spd > 5:
            chill = round(13.12 +  (.6215 * out)- (11.37 * pow(spd,.16))+ (.3965 * out * pow(spd,.16)),1)
            if chill < out:
                
                t_chill.set("{0:.1f} C ".format(chill))
                l_chill.set("CHILL:")
                s_chill.set("TM.TLabel")
            else:
                t_chill.set("{0:.1f} C ".format(dew))
                l_chill.set("DEW :")
                s_chill.set("BM.TLabel")                
            
            
        else:
            t_chill.set("{0:.1f} C ".format(dew))
            l_chill.set("DEW :")
            s_chill.set("BM.TLabel")
        t_dew.set("{0:.1f} C ".format(dew))
        t_max.set("{0:.1f} C ".format(out))
        t_hum.set("{0:.1f} %".format(rel))
        
        pabs = float(int(p_split[2]) + (256 * int(p_split[1])))/100
        alt = float(int(p_split[3]) + (256 * int(p_split[4])))
        prel = float(int(p_split[6]) + (256 * int(p_split[5])))/100
        ptrend = float(int(p_split[7]))
        ##Deterime if preassure is rising then add 5
        if float(int(p_split[8]))== 1 and float(int(p_split[7])) > 0:
            ptrend = float(int(p_split[7]))+ 5
        
        p_avg.set("{0:.1f} kPa".format(pabs))

        lum = float(int(s_split[2]) + (256 * int(s_split[1])))
        uv = float(s_split[3])
        rad = round(float(int(s_split[5]) + (256 * int(s_split[4]))),0)
        if rad == 0:
            rad = round(lum * .0079,0)
        if lum == 0:
            lum = round(rad * 126.58,0)
                                       
        sr_avg.set("{0:.0f} W/m2".format(rad))
        sr_uv.set(getuv(uv))
        sr_eng.set(SolarEnergy + " Ly")
        sr_hrs.set("{0:.1f} %".format(float(Cloud))) 
        Rain_RateB = round(((float(r_split[1]) * 100) + float(r_split[2]))/100,1)
        Rain_Today = round(((float(r_split[3]) * 100) + float(r_split[4]))/10,1)
        Rain_Yesterday = round(((float(r_split[5])  * 100) + float(r_split[6]))/10,1)
        Rain_Tips = round(float(r_split[7]) + (float(r_split[8])* 100),0)
        if Rain_RateB > .1:
            r_rate.set("{0:.1f} mm".format(Rain_RateB))
        else:
            r_rate.set("")

        if Rain_Today > 0:
            r_today.set("{0:.1f} mm".format(Rain_Today))
        else:
            r_today.set("")
        if Rain_Yesterday > 0:
            r_yest.set("{0:.1f} mm".format(Rain_Yesterday))
        else:
            r_yest.set("")
        if Rain_Tips > 0:
            r_tips.set("{0:.0f}".format(Rain_Tips))
        else:
            r_tips.set("")

        subprocess.call(["xdotool","key","F2"])
        root.after(10000, getweather)


    except :
        strError.set("No Connection")
        t_dew.set("")
        t_max.set("")
        t_hum.set("")
        t_chill.set("")
        l_chill.set("DEW :")
        p_avg.set("")
        sr_avg.set("")
        sr_uv.set("")
        sr_eng.set("")
        sr_hrs.set("")
        w_spd.set("")
        w_dir.set("")
        w_10min.set("")
        w_gust.set("")
        version.set("")
        eor_version.set("")
        eos_version.set("")
        r_rate.set("")
        r_today.set("")
        r_yest.set("")
        r_tips.set("")
        r_7days.set("")
        r_30days.set("")
        fanState.set("")
        cabTemp.set("")
        battery.set("")
        source.set("")
        feedCount.set("")
        feedTime.set("")
        archived.set("")
        root.after(10000, getweather)
            
 
root = tk.Tk()
root.configure(background="black")
root.title("EOS Weather")
img = ImageTk.PhotoImage(file='/var/www/img/eos.ico')
root.tk.call('wm','iconphoto', root._w, img)


mainframe = tk.Frame(root)
mainframe.configure(background="black")
mainframe.grid(column=0, row=0, sticky=("N, W, E, S"))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)


## Make Tabs
n = ttk.Notebook(mainframe)
tab1 = ttk.Frame(n, style="BM.TFrame")
tab2 = ttk.Frame(n, style="BM.TFrame")
tab3 = ttk.Frame(n, style="BM.TFrame")
tab4 = ttk.Frame(n, style="BM.TFrame")
tab5 = ttk.Frame(n, style="BM.TFrame")
tab6 = ttk.Frame(n, style="BM.TFrame")
tab7 = ttk.Frame(n, style="BM.TFrame")

img1 = geticon("/var/www/img/weather256.png")
img2 = geticon("/var/www/img/wind_flag_storm.png")
img3 = geticon("/var/www/img/line_chart.png")
img4 = geticon("/var/www/img/xml.png")
img5 = geticon("/var/www/img/good.png")
img6 = geticon("/var/www/img/no_network.png")
img7 = geticon("/var/www/img/w-s-watch.gif")

n.add(tab1, text='Station', image = img1, compound='top')
n.add(tab2, text='Readings', image = img2, compound='top')
n.add(tab3, text ='Charts', image = img3, compound='top')
n.add(tab4, text = 'Reports', image = img4, compound='top')

n.add(tab6, text = 'Tables', image = img6, compound='top')

n.add(tab7, text = 'Alarms', image = img7, compound='top')
n.add(tab5, text = 'Summary', image = img5, compound='top')

## Variables
server = tk.StringVar()
strError = tk.StringVar()
version = tk.StringVar()
eor_version = tk.StringVar()
eos_version = tk.StringVar()
t_dew = tk.StringVar()
t_max = tk.StringVar()
t_hum = tk.StringVar()
t_chill = tk.StringVar()
l_chill = tk.StringVar()
s_chill = tk.StringVar()
p_avg = tk.StringVar()
sr_avg = tk.StringVar()
sr_uv = tk.StringVar()
sr_eng = tk.StringVar()
sr_hrs = tk.StringVar()

w_spd = tk.StringVar()
w_dir = tk.StringVar()
w_gust = tk.StringVar()
w_10min = tk.StringVar()

r_rate = tk.StringVar()
r_today = tk.StringVar()
r_yest = tk.StringVar()
r_tips = tk.StringVar()
r_1days = tk.StringVar()
r_7days = tk.StringVar()
r_30days = tk.StringVar()

stationval = tk.StringVar()
reportval = tk.StringVar()
tableval = tk.StringVar()
graphval = tk.StringVar()

fanState = tk.StringVar()
cabTemp = tk.StringVar()
battery = tk.StringVar()
source = tk.StringVar()
feedCount = tk.StringVar()
feedTime = tk.StringVar()
archived = tk.StringVar()

d_lowTemp = tk.StringVar()
d_hiTemp = tk.StringVar()
d_lowPress = tk.StringVar()
d_hiPress = tk.StringVar()
d_avgWind = tk.StringVar()
d_hiWind = tk.StringVar()
d_runWind = tk.StringVar()
d_sun = tk.StringVar()
w_lowTemp = tk.StringVar()
w_hiTemp = tk.StringVar()
w_lowPress = tk.StringVar()
w_hiPress = tk.StringVar()
w_avgWind = tk.StringVar()
w_hiWind = tk.StringVar()
w_sun = tk.StringVar()
wd_lowTemp = tk.StringVar()
wd_hiTemp = tk.StringVar()
wd_lowPress = tk.StringVar()
wd_hiPress = tk.StringVar()
wd_hiWind = tk.StringVar()
wd_sun = tk.StringVar()
m_lowTemp = tk.StringVar()
m_hiTemp = tk.StringVar()
m_lowPress = tk.StringVar()
m_hiPress = tk.StringVar()
m_avgWind = tk.StringVar()
m_hiWind = tk.StringVar()
m_sun = tk.StringVar()
md_lowTemp = tk.StringVar()
md_hiTemp = tk.StringVar()
md_lowPress = tk.StringVar()
md_hiPress = tk.StringVar()
md_hiWind = tk.StringVar()
md_sun = tk.StringVar()
forG1 = "white"
backG1 = "black"
forG2 = "yellow"
backG2 = "lavender"
forG3 = "red"
forG4 = "blue"
forG5 = "yellow"
forG6 = "tomato"
forG7 = "green"
backG3 = "yellow"
backG4 = "blue"

## Configure styles
moduleStyle = ttk.Style()
moduleStyle.configure("BM.TFrame", foreground=forG1, background=backG1)
moduleStyle.configure("BM.TLabelframe", foreground=forG1, background=backG1)
moduleStyle.configure("BM.TLabelframe.Label", foreground=forG1, background=backG1, font=("helvetica", 12))
moduleStyle.configure("BM.TCombobox.Listbox", foreground=forG1, background=backG1, font=("helvetica", 12))
moduleStyle.configure("BM.Listbox", foreground=forG1, background=backG1, font=("helvetica", 8))
moduleStyle.configure("BM.TLabel", foreground=forG2, background=backG1 , font=("helvetica", 10))
moduleStyle.configure("M.TLabel", foreground=forG1, background=backG1 , font=("helvetica", 16))
moduleStyle.configure("G.TLabel", foreground=forG7, background=backG2 , font=("helvetica", 12))
moduleStyle.configure("M1.TLabel", foreground=forG2, background=backG1 , font=("helvetica", 16))
moduleStyle.configure("M3.TLabel", foreground=forG6, background=backG1 , font=("helvetica", 16))
moduleStyle.configure("M2.TLabel", foreground=forG1, background=backG1 , font=("helvetica", 16))
moduleStyle.configure("TM.TLabel", foreground=forG1, background=backG1 , font=("helvetica", 34))
moduleStyle.configure("CM.TLabel", foreground=forG1, background=backG1 , font=("helvetica", 28))
moduleStyle.configure("SM.TLabelframe", foreground=forG1, background=backG1)
moduleStyle.configure("SM.TLabelframe.Label", foreground=forG1, background=backG1, font=("helvetica", 12))
moduleStyle.configure("SM.TLabel", foreground=forG5, background=backG1 , font=("helvetica", 34))
moduleStyle.configure("VM.TLabel", foreground=forG5, background=backG1 , font=("helvetica", 28))
moduleStyle.configure("WM.TLabelframe", foreground=forG1, background=backG1)
moduleStyle.configure("WM.TLabel", foreground=forG1, background=backG1 , font=("helvetica", 34))
moduleStyle.configure("GM.TLabel", foreground=forG1, background=backG1 , font=("helvetica", 28))
moduleStyle.configure("WM.TLabelframe.Label", foreground=forG1, background=backG1, font=("helvetica", 12))
moduleStyle.configure("RM.TLabelframe", foreground=forG1, background=backG1)
moduleStyle.configure("RM.TLabelframe.Label", foreground=forG1, background=backG1, font=("helvetica", 12))
moduleStyle.configure("RM.TLabel", foreground=forG1, background=backG4 , font=("helvetica", 20))
bigfont = tkf.Font(family='helvetica',size=16)
midfont = tkf.Font(family='helvetica',size=12)
root.option_add('*TCombobox*Listbox*Font',bigfont)


## icons
logonicon = geticon("/var/www/img/graph.png")
upicon = geticon("/var/www/img/arrow_up.png")
downicon = geticon("/var/www/img/arrow_down.png")
exiticon = geticon("/var/www/img/down.png")

## Buttons
ttk.Button(tab1, text="Connect", image=logonicon, command=getweather, compound="bottom").grid(column=10, row=2, sticky="S, W")
ttk.Button(tab1, text="Exit", command=quit, image=exiticon, compound="top").grid(column=10, row=3, sticky="N, W")
ttk.Button(tab3, text="Get Chart", command=docharts, image=downicon, compound="left").grid(column=1, row=0, sticky="W")
ttk.Button(tab4, text="Get NOAA Report", command=donoaareport, image=downicon, compound="left").grid(column=1, row=0, sticky="W")
ttk.Button(tab6, text="Get Source Table", command=dotable, image=upicon, compound="left").grid(column=1, row=0, sticky="W")
ttk.Button(tab7, text="Get Alarms", command=getalarms, image=downicon, compound="left").grid(column=0, row=0, sticky="W")
ttk.Button(tab5, text="Get Summary", command=dosummary, image=downicon, compound="left").grid(column=0, row=0, sticky="W")

## Lists

stationlist = ttk.Combobox(tab1, textvariable=stationval, font=bigfont, state='readonly')
stations, stationId = eosp.getstations()
stationlist['values'] = (stations)
stationlist.current(0)
stationlist.grid(column=0, row=0, sticky="W, N")

reportlist = ttk.Combobox(tab4, textvariable=reportval, font=bigfont, state='readonly')
reportlist['values'] = ('NOAA Month','NOAA Previous Month','NOAA Year','NOAA Previous Year')
reportlist.current(0)
reportlist.grid(column=0, row=0, sticky="W, N")

tablelist = ttk.Combobox(tab6, textvariable=tableval, font=bigfont, state='readonly')
tablelist['values'] = ('N/A')
tablelist.current(0)
tablelist.grid(column=0, row=0, sticky="W, N")

graphlist = ttk.Combobox(tab3, textvariable=graphval, font=bigfont, state='readonly')
graphlist['values'] = ('Board','Pressure','Solar','Temp','Wind')
graphlist.current(0)
graphlist.grid(column=0, row=0, sticky="W, N")

## Labels
strError.set("IP Address of Station")
ttk.Label(tab1, textvariable=strError, style="G.TLabel").grid(column=0, row=1, sticky=("W, E"))
##ttk.Label(tab1, text="  Local IP Address of Station", style="G.TLabel").grid(column=1, row=2, sticky=("W, E"))
## Tab 1 Station

##server_entry = ttk.Entry(tab1, width=20, textvariable=server, font=midfont)
##server.set(eoss.SQL.server)
##server_entry.grid(column=0, row=2, sticky=("W, E"))


Modules = ttk.Labelframe(tab1, text='Modules', style="BM.TLabelframe")
Modules.grid(column=0, row=3, sticky=("N"))

ttk.Label(Modules, text="Firmware Version : ", style="BM.TLabel").grid(column=0, row=2, sticky="E")
ttk.Label(Modules, textvariable=version, style="M.TLabel").grid(column=1, row=2, sticky=("W, E"))
##ttk.Label(Modules, text="Eos Version : ", style="BM.TLabel").grid(column=0, row=3, sticky="E")
##ttk.Label(Modules, textvariable=eos_version, style="M.TLabel").grid(column=1, row=3, sticky=("W, E"))
##ttk.Label(Modules, text="Eos Version : ", style="BM.TLabel").grid(column=0, row=4, sticky="E")
##ttk.Label(Modules, textvariable=eos_version, style="M.TLabel").grid(column=1, row=4, sticky=("W, E"))


stationModule = ttk.Labelframe(tab1, text='Station Status', style="BM.TLabelframe")
stationModule.grid(column=1, row=3, sticky=("N"))
##ttk.Label(stationModule, text="Fan State : ", style="BM.TLabel").grid(column=0, row=1, sticky="E")
##ttk.Label(stationModule, textvariable=fanState, style="M.TLabel").grid(column=1, row=1, sticky=("W, E"))
ttk.Label(stationModule, text="Cabinet Temp : ", style="BM.TLabel").grid(column=0, row=2, sticky="E")
ttk.Label(stationModule, textvariable=cabTemp, style="M.TLabel").grid(column=1, row=2, sticky=("W, E"))
ttk.Label(stationModule, text="Battery : ", style="BM.TLabel").grid(column=0, row=3, sticky="E")
ttk.Label(stationModule, textvariable=battery, style="M.TLabel").grid(column=1, row=3, sticky=("W, E"))
ttk.Label(stationModule, text="Source : ", style="BM.TLabel").grid(column=0, row=4, sticky="E")
ttk.Label(stationModule, textvariable=source, style="M.TLabel").grid(column=1, row=4, sticky=("W, E"))
##ttk.Label(stationModule, text="Feed Count : ", style="BM.TLabel").grid(column=0, row=5, sticky="E")
##ttk.Label(stationModule, textvariable=feedCount, style="M.TLabel").grid(column=1, row=5, sticky=("W, E"))
ttk.Label(stationModule, text="Feed Time : ", style="BM.TLabel").grid(column=0, row=6, sticky="E")
ttk.Label(stationModule, textvariable=feedTime, style="M.TLabel").grid(column=1, row=6, sticky=("W, E"))
ttk.Label(stationModule, text="Archived : ", style="BM.TLabel").grid(column=0, row=7, sticky="E")
ttk.Label(stationModule, textvariable=archived, style="M.TLabel").grid(column=1, row=7, sticky=("W, E"))

## Tab 2  Instuments
baseModule = ttk.Labelframe(tab2, text='Base Module', style="BM.TLabelframe")
baseModule.grid(column=0, row=0, sticky=("N"))
ttk.Label(baseModule, text='TMP : ', style="BM.TLabel").grid(column=0, row=1, sticky=("E"))
ttk.Label(baseModule, textvariable=t_max, style="TM.TLabel").grid(column=1, row=1, sticky=("W"))

ttk.Label(baseModule, textvariable=l_chill, style="BM.TLabel").grid(column=0, row=2, sticky=("E"))
ttk.Label(baseModule, textvariable=t_chill, style="CM.TLabel").grid(column=1, row=2, sticky=("W"))
ttk.Label(baseModule, text='HUM : ', style="BM.TLabel").grid(column=0, row=3, sticky=("E"))
ttk.Label(baseModule, textvariable=t_hum, style="TM.TLabel").grid(column=1, row=3, sticky=("W"))
ttk.Label(baseModule, text='PRE : ', style="BM.TLabel").grid(column=0, row=4, sticky=("E"))
ttk.Label(baseModule, textvariable=p_avg, style="TM.TLabel").grid(column=1, row=4, sticky=("W"))

solarModule = ttk.Labelframe(tab2, text='Solar Module', style="SM.TLabelframe")
solarModule.grid(column=2, row=0, sticky=("N"))
ttk.Label(solarModule, text='RAD : ', style="BM.TLabel").grid(column=0, row=1, sticky=("E"))
ttk.Label(solarModule, textvariable=sr_avg, style="SM.TLabel").grid(column=1, row=1, sticky=("E,W"))
ttk.Label(solarModule, text='UV : ', style="BM.TLabel").grid(column=0, row=2, sticky=("E"))
ttk.Label(solarModule, textvariable=sr_uv, style="VM.TLabel").grid(column=1, row=2, sticky=("E,W"))
ttk.Label(solarModule, text='ENG : ', style="BM.TLabel").grid(column=0, row=3, sticky=("E"))
ttk.Label(solarModule, textvariable=sr_eng, style="SM.TLabel").grid(column=1, row=3, sticky=("E,W"))
ttk.Label(solarModule, text='CLD : ', style="BM.TLabel").grid(column=0, row=4, sticky=("E"))
ttk.Label(solarModule, textvariable=sr_hrs, style="SM.TLabel").grid(column=1, row=4, sticky=("E,W"))

windModule = ttk.Labelframe(tab2, text='Wind Module', style="WM.TLabelframe")
windModule.grid(column=5, row=0, sticky=("N"))
ttk.Label(windModule, text='DIR : ', style="BM.TLabel").grid(column=0, row=1, sticky=("E"))
ttk.Label(windModule, textvariable=w_dir, style="WM.TLabel").grid(column=1, row=1, sticky=("W, E"))
ttk.Label(windModule, text='SPD : ', style="BM.TLabel").grid(column=0, row=2, sticky=("E"))
ttk.Label(windModule, textvariable=w_spd, style="WM.TLabel").grid(column=1, row=2, sticky=("W, E"))
ttk.Label(windModule, text='AVG : ', style="BM.TLabel").grid(column=0, row=3, sticky=("E"))
ttk.Label(windModule, textvariable=w_10min, style="WM.TLabel").grid(column=1, row=3, sticky=("W, E"))
ttk.Label(windModule, text='GUST : ', style="BM.TLabel").grid(column=0, row=4, sticky=("E"))
ttk.Label(windModule, textvariable=w_gust, style="GM.TLabel").grid(column=1, row=4, sticky=("W, E"))

rainModule = ttk.Labelframe(tab2, text='Rain Module', style="RM.TLabelframe")
rainModule.grid(column=0, row=1, sticky=("N"))
ttk.Label(rainModule, text='RATE : ', style="BM.TLabel").grid(column=0, row=1, sticky=("E"))
ttk.Label(rainModule, textvariable=r_rate, style="RM.TLabel").grid(column=1, row=1, sticky=("W, E"))
ttk.Label(rainModule, text='TODAY : ', style="BM.TLabel").grid(column=0, row=2, sticky=("E"))
ttk.Label(rainModule, textvariable=r_today, style="RM.TLabel").grid(column=1, row=2, sticky=("W, E"))
ttk.Label(rainModule, text='YESTER : ', style="BM.TLabel").grid(column=0, row=3, sticky=("E"))
ttk.Label(rainModule, textvariable=r_yest, style="RM.TLabel").grid(column=1, row=3, sticky=("W, E"))
ttk.Label(rainModule, text='TIPS : ', style="BM.TLabel").grid(column=0, row=4, sticky=("E"))
ttk.Label(rainModule, textvariable=r_tips, style="RM.TLabel").grid(column=1, row=4, sticky=("W, E"))
##ttk.Label(rainModule, text='7 DAY : ', style="BM.TLabel").grid(column=0, row=5, sticky=("E"))
##ttk.Label(rainModule, textvariable=r_7days, style="RM.TLabel").grid(column=1, row=5, sticky=("W, E"))
##ttk.Label(rainModule, text='30 DAY : ', style="BM.TLabel").grid(column=0, row=6, sticky=("E"))
##ttk.Label(rainModule, textvariable=r_30days, style="RM.TLabel").grid(column=1, row=6, sticky=("W, E"))

## Tab 3 Charts

## Tab 4 Reports

## Tab 5 Summary

dailyLabel = ttk.Labelframe(tab5, text="Reading", style="BM.TLabelframe")
dailyLabel.grid(column=0, row=1, sticky=("N"))
ttk.Label(dailyLabel, text='Low Temp', style="M1.TLabel").grid(column=0, row=1, sticky=("E,W"))
ttk.Label(dailyLabel, text='High Temp', style="M1.TLabel").grid(column=0, row=2, sticky=("E,W"))
ttk.Label(dailyLabel, text='Low Pressure', style="M1.TLabel").grid(column=0, row=3, sticky=("E,W"))
ttk.Label(dailyLabel, text='High Pressure', style="M1.TLabel").grid(column=0, row=4, sticky=("E,W"))
ttk.Label(dailyLabel, text='Average Wind', style="M1.TLabel").grid(column=0, row=5, sticky=("E,W"))
ttk.Label(dailyLabel, text='Hi Wind', style="M1.TLabel").grid(column=0, row=6, sticky=("E,W"))
ttk.Label(dailyLabel, text='Wind Run', style="M1.TLabel").grid(column=0, row=7, sticky=("E,W"))
##ttk.Label(dailyLabel, text='Sunlight', style="M1.TLabel").grid(column=0, row=8, sticky=("E,W"))
ttk.Label(dailyLabel, text='Rain Fall', style="M1.TLabel").grid(column=0, row=9, sticky=("E,W"))

dailyReport = ttk.Labelframe(tab5, text="Today", style="BM.TLabelframe")
dailyReport.grid(column=1, row=1, sticky=("N"))
ttk.Label(dailyReport, textvariable=d_lowTemp, style="M.TLabel").grid(column=0, row=1, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=d_hiTemp, style="M2.TLabel").grid(column=0, row=2, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=d_lowPress, style="M.TLabel").grid(column=0, row=3, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=d_hiPress, style="M2.TLabel").grid(column=0, row=4, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=d_avgWind, style="M.TLabel").grid(column=0, row=5, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=d_hiWind, style="M2.TLabel").grid(column=0, row=6, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=d_runWind, style="M.TLabel").grid(column=0, row=7, sticky=("W, E"))
##ttk.Label(dailyReport, textvariable=d_sun, style="M2.TLabel").grid(column=0, row=8, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=r_1days, style="M.TLabel").grid(column=0, row=9, sticky=("W, E"))

weekReport = ttk.Labelframe(tab5, text="7 days", style="BM.TLabelframe")
weekReport.grid(column=2, row=1, sticky=("N"))
ttk.Label(weekReport, textvariable=w_lowTemp, style="M.TLabel").grid(column=0, row=1, sticky=("W, E"))
ttk.Label(weekReport, textvariable=w_hiTemp, style="M2.TLabel").grid(column=0, row=2, sticky=("W, E"))
ttk.Label(weekReport, textvariable=w_lowPress, style="M.TLabel").grid(column=0, row=3, sticky=("W, E"))
ttk.Label(weekReport, textvariable=w_hiPress, style="M2.TLabel").grid(column=0, row=4, sticky=("W, E"))
ttk.Label(weekReport, textvariable=w_avgWind, style="M.TLabel").grid(column=0, row=5, sticky=("W, E"))
ttk.Label(weekReport, textvariable=w_hiWind, style="M2.TLabel").grid(column=0, row=6, sticky=("W, E"))
ttk.Label(weekReport, text= "", style="M1.TLabel").grid(column=0, row=7, sticky=("W, E"))
##ttk.Label(weekReport, textvariable=w_sun, style="M2.TLabel").grid(column=0, row=8, sticky=("W, E"))
ttk.Label(weekReport, textvariable=r_7days, style="M.TLabel").grid(column=0, row=9, sticky=("W, E"))

weekDateReport = ttk.Labelframe(tab5, text="on", style="BM.TLabelframe")
weekDateReport.grid(column=3, row=1, sticky=("N"))
ttk.Label(weekDateReport, textvariable=wd_lowTemp, style="M3.TLabel").grid(column=0, row=1, sticky=("W, E"))
ttk.Label(weekDateReport, textvariable=wd_hiTemp, style="M3.TLabel").grid(column=0, row=2, sticky=("W, E"))
ttk.Label(weekDateReport, textvariable=wd_lowPress, style="M3.TLabel").grid(column=0, row=3, sticky=("W, E"))
ttk.Label(weekDateReport, textvariable=wd_hiPress, style="M3.TLabel").grid(column=0, row=4, sticky=("W, E"))
ttk.Label(weekDateReport, text="", style="M3.TLabel").grid(column=0, row=5, sticky=("W, E"))
ttk.Label(weekDateReport, textvariable=wd_hiWind, style="M3.TLabel").grid(column=0, row=6, sticky=("W, E"))
ttk.Label(weekDateReport, text= "", style="M3.TLabel").grid(column=0, row=7, sticky=("W, E"))
##ttk.Label(weekDateReport, textvariable=wd_sun, style="M3.TLabel").grid(column=0, row=8, sticky=("W, E"))
ttk.Label(weekDateReport, text="", style="M3.TLabel").grid(column=0, row=9, sticky=("W, E"))

monthReport = ttk.Labelframe(tab5, text="30 days", style="BM.TLabelframe")
monthReport.grid(column=4, row=1, sticky=("N"))
ttk.Label(monthReport, textvariable=m_lowTemp, style="M.TLabel").grid(column=1, row=1, sticky=("W, E"))
ttk.Label(monthReport, textvariable=m_hiTemp, style="M2.TLabel").grid(column=1, row=2, sticky=("W, E"))
ttk.Label(monthReport, textvariable=m_lowPress, style="M.TLabel").grid(column=1, row=3, sticky=("W, E"))
ttk.Label(monthReport, textvariable=m_hiPress, style="M2.TLabel").grid(column=1, row=4, sticky=("W, E"))
ttk.Label(monthReport, textvariable=m_avgWind, style="M.TLabel").grid(column=1, row=5, sticky=("W, E"))
ttk.Label(monthReport, textvariable=m_hiWind, style="M2.TLabel").grid(column=1, row=6, sticky=("W, E"))
ttk.Label(monthReport, text="", style="M.TLabel").grid(column=1, row=7, sticky=("W, E"))
##ttk.Label(monthReport, textvariable=m_sun, style="M2.TLabel").grid(column=1, row=8, sticky=("W, E"))
ttk.Label(monthReport, textvariable=r_30days, style="M.TLabel").grid(column=1, row=9, sticky=("W, E"))

monthDateReport = ttk.Labelframe(tab5, text="on", style="BM.TLabelframe")
monthDateReport.grid(column=5, row=1, sticky=("N"))
ttk.Label(monthDateReport, textvariable=md_lowTemp, style="M3.TLabel").grid(column=1, row=1, sticky=("W, E"))
ttk.Label(monthDateReport, textvariable=md_hiTemp, style="M3.TLabel").grid(column=1, row=2, sticky=("W, E"))
ttk.Label(monthDateReport, textvariable=md_lowPress, style="M3.TLabel").grid(column=1, row=3, sticky=("W, E"))
ttk.Label(monthDateReport, textvariable=md_hiPress, style="M3.TLabel").grid(column=1, row=4, sticky=("W, E"))
ttk.Label(monthDateReport, text="", style="M3.TLabel").grid(column=1, row=5, sticky=("W, E"))
ttk.Label(monthDateReport, textvariable=md_hiWind, style="M3.TLabel").grid(column=1, row=6, sticky=("W, E"))
ttk.Label(monthDateReport, text= "", style="M3.TLabel").grid(column=1, row=7, sticky=("W, E"))
##ttk.Label(monthDateReport, textvariable=md_sun, style="M3.TLabel").grid(column=1, row=8, sticky=("W, E"))
ttk.Label(monthDateReport, text= "", style="M3.TLabel").grid(column=1, row=9, sticky=("W, E"))

## Tab 6 Reports
ttk.Label(tab6, text='Table opens in web brower', style="M1.TLabel").grid(column=0, row=1, sticky=("E,W"))

## Tab7 Alarms
listalarm = tk.Listbox(tab7, font=midfont, width=80)
listalarm.grid(column=0, row=1)

## Clean UP and set window size
for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)
getweather()


##server_entry.focus()
root.bind('<Return>', getweather)
##root.attributes('-fullscreen', True)
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (800,480))
## RUN
root.mainloop()
