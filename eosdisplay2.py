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
import MySQLdb as mdb
import Tkinter as tk
import ttk
import tkFont as tkf
from PIL import Image
from PIL import ImageTk
import StringIO as cS
import urllib
import webbrowser


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

        webbrowser.open(URL)
        
    except:
        pass

def donoaareport(*args):
    try:
        noaaReport = ttk.Labelframe(tab4, text=  reportval.get(), style="BM.TLabelframe")
        noaaReport.grid(column=1, row=2, sticky=("N"))
        if reportval.get() == 'NOAA Month':
            URL = "http://" + server.get() + "/reports/NOAAMO.TXT"
        elif reportval.get() == 'NOAA Year':
            URL = "http://" + server.get() + "/reports/NOAAYR.TXT"
        elif reportval.get() == 'NOAA Previous Year':
            URL = "http://" + server.get() + "/reports/NOAAPRYR.TXT"
        elif reportval.get() == 'NOAA Previous Month':
            URL = "http://" + server.get() + "/reports/NOAAPRMO.TXT"
        else:
            URL = ''
        u = urllib.urlopen(URL)
        raw_data = u.read()       
        noaatext = tk.Text(noaaReport, height=40, width=85)
        noaatext.grid(column=0, row=2)
        noaatext.insert("1.0", raw_data)
        noaatext.pack()
        
    except:
        pass

def dosummary(*args):

    try:
        db = mdb.connect(host= server.get(), port = eoss.SQL.port, user= eoss.SQL.user,passwd= eoss.SQL.password, db= eoss.SQL.database)
        cur = db.cursor(mdb.cursors.DictCursor)
        try:
            cur.execute("SELECT WIND_RUN as WRUN, WIND_AVG as WAVG, WIND_HI as WHI, ROUND(BAR_HI/10,1) as MAXBAR,  ROUND(BAR_LOW/10,1) as MINBAR, TEMP_LOW as LOWT, TEMP_HI as HIT FROM CORE_DATE WHERE WE_DATE > DATE_SUB(SYSDATE(), INTERVAL 1 DAY)")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                d_lowTemp.set("{0:.1f} C ".format(float(row["LOWT"])))
                d_hiTemp.set("{0:.1f} C ".format(float(row["HIT"])))
                d_lowPress.set("{0:.1f} kPa ".format(row["MINBAR"]))
                d_hiPress.set("{0:.1f} kPa ".format(row["MAXBAR"]))
                d_avgWind.set("{0:.1f} km/h ".format(float(row["WAVG"])))
                d_hiWind.set("{0:.1f} km/h ".format(float(row["WHI"])))
                d_runWind.set("{0:.1f} km ".format(float(row["WRUN"])))

            cur.execute("SELECT ROUND(AVG(CAST(WIND_AVG as DECIMAL(10,2))),1) as WAVG, MAX(CAST(WIND_HI as DECIMAL(10,1))) as WHI, MAX(CAST(BAR_HI as DECIMAL(10,1))) as MAXBAR,  MIN(CAST(BAR_LOW as DECIMAL(10,1))) as MINBAR, MIN(CAST(TEMP_LOW as DECIMAL(10,1))) as LOWT, MAX(CAST(TEMP_HI as DECIMAL(10,1))) as HIT FROM CORE_DATE where WE_DATE > DATE_SUB(sysdate(),INTERVAL 7 DAY)")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                lowt = row["LOWT"]
                hit = row["HIT"]
                minbar = row["MINBAR"]
                maxbar = row["MAXBAR"]
                hiw = row["WHI"]
                w_lowTemp.set("{0:.1f} C ".format(row["LOWT"]))

                w_hiTemp.set("{0:.1f} C ".format(row["HIT"]))

                w_lowPress.set("{0:.1f} kPa ".format(row["MINBAR"]/10))

                w_hiPress.set("{0:.1f} kPa ".format(row["MAXBAR"]/10))
                w_avgWind.set("{0:.1f} km/h ".format(row["WAVG"]))

                w_hiWind.set("{0:.1f} km/h ".format(row["WHI"]))
                
            cur.execute("SELECT WE_DATE FROM CORE_DATE where  TEMP_LOW = " + str(lowt)  + " AND  WE_DATE > DATE_SUB(sysdate(),INTERVAL 7 DAY) order by WE_DATE desc limit 0,1")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                wd_lowTemp.set(row["WE_DATE"])

            cur.execute("SELECT WE_DATE FROM CORE_DATE where  TEMP_HI = " + str(hit)  + " AND  WE_DATE > DATE_SUB(sysdate(),INTERVAL 7 DAY) order by WE_DATE desc limit 0,1")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                wd_hiTemp.set(row["WE_DATE"])

            cur.execute("SELECT WE_DATE FROM CORE_DATE where  BAR_HI = " + str(maxbar)  + " AND  WE_DATE > DATE_SUB(sysdate(),INTERVAL 7 DAY) order by WE_DATE desc limit 0,1")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                wd_hiPress.set(row["WE_DATE"])
            cur.execute("SELECT WE_DATE FROM CORE_DATE where  BAR_LOW = " + str(minbar)  + " AND  WE_DATE > DATE_SUB(sysdate(),INTERVAL 7 DAY) order by WE_DATE desc limit 0,1")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                wd_lowPress.set(row["WE_DATE"])
            cur.execute("SELECT WE_DATE FROM CORE_DATE where  WIND_HI = " + str(hiw)  + " AND  WE_DATE > DATE_SUB(sysdate(),INTERVAL 7 DAY) order by WE_DATE desc limit 0,1")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                wd_hiWind.set(row["WE_DATE"])
                


            cur.execute("SELECT ROUND(AVG(CAST(WIND_AVG as DECIMAL(10,2))),1) as WAVG, MAX(CAST(WIND_HI as DECIMAL(10,1))) as WHI, MAX(CAST(BAR_HI as DECIMAL(10,1))) as MAXBAR,  MIN(CAST(BAR_LOW as DECIMAL(10,1))) as MINBAR, MIN(CAST(TEMP_LOW as DECIMAL(10,1))) as LOWT, MAX(CAST(TEMP_HI as DECIMAL(10,1))) as HIT FROM CORE_DATE where WE_DATE > DATE_SUB(sysdate(),INTERVAL 30 DAY)")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                lowt = row["LOWT"]
                hit = row["HIT"]
                minbar = row["MINBAR"]
                maxbar = row["MAXBAR"]
                hiw = row["WHI"]
                m_lowTemp.set("{0:.1f} C ".format(row["LOWT"]))
                m_hiTemp.set("{0:.1f} C ".format(row["HIT"]))
                m_lowPress.set("{0:.1f} kPa ".format(row["MINBAR"]/10))
                m_hiPress.set("{0:.1f} kPa ".format(row["MAXBAR"]/10))
                m_avgWind.set("{0:.1f} km/h ".format(row["WAVG"]))
                m_hiWind.set("{0:.1f} km/h ".format(row["WHI"]))


                 
            cur.execute("SELECT WE_DATE FROM CORE_DATE where  TEMP_LOW = " + str(lowt)  + " AND  WE_DATE > DATE_SUB(sysdate(),INTERVAL 30 DAY) order by WE_DATE desc limit 0,1")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                md_lowTemp.set(row["WE_DATE"])

            cur.execute("SELECT WE_DATE FROM CORE_DATE where  TEMP_HI = " + str(hit)  + " AND  WE_DATE > DATE_SUB(sysdate(),INTERVAL 30 DAY) order by WE_DATE desc limit 0,1")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                md_hiTemp.set(row["WE_DATE"])

            cur.execute("SELECT WE_DATE FROM CORE_DATE where  BAR_HI = " + str(maxbar)  + " AND  WE_DATE > DATE_SUB(sysdate(),INTERVAL 30 DAY) order by WE_DATE desc limit 0,1")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                md_hiPress.set(row["WE_DATE"])
            cur.execute("SELECT WE_DATE FROM CORE_DATE where  BAR_LOW = " + str(minbar)  + " AND  WE_DATE > DATE_SUB(sysdate(),INTERVAL 30 DAY) order by WE_DATE desc limit 0,1")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                md_lowPress.set(row["WE_DATE"])
            cur.execute("SELECT WE_DATE FROM CORE_DATE where  WIND_HI = " + str(hiw)  + " AND  WE_DATE > DATE_SUB(sysdate(),INTERVAL 30 DAY) order by WE_DATE desc limit 0,1")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                md_hiWind.set(row["WE_DATE"])              

            cur.execute("SELECT CAST(SUN_HRS as DECIMAL(10,1)) as S FROM CORE_DATE where WE_DATE > DATE_SUB(sysdate(),INTERVAL 1 DAY)")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                d_sun.set("{0:.1f} hrs ".format(row["S"]))            

            cur.execute("SELECT SUM(CAST(SUN_HRS as DECIMAL(10,1))) as S, ROUND(AVG(CAST(SUN_HRS as DECIMAL(10,1))),1) as SAVG FROM CORE_DATE where WE_DATE > DATE_SUB(sysdate(),INTERVAL 7 DAY)")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                w_sun.set("{0:.1f} hrs ".format(row["S"]))
                wd_sun.set("{0:.1f} per day ".format(row["SAVG"]))
            cur.execute("SELECT SUM(CAST(SUN_HRS as DECIMAL(10,1))) as S, ROUND(AVG(CAST(SUN_HRS as DECIMAL(10,1))),1) as SAVG FROM CORE_DATE where WE_DATE > DATE_SUB(sysdate(),INTERVAL 30 DAY)")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                m_sun.set("{0:.1f} hrs ".format(row["S"]))
                md_sun.set("{0:.1f} per day ".format(row["SAVG"]))
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
    tempReport = ttk.Labelframe(tab3, text="Temperature", style="BM.TLabelframe")
    tempReport.grid(column=0, row=1, sticky=("N"))   
    tempphoto = getimage("/var/www/reports/temp.png")
    templabel = ttk.Label(tempReport, image=tempphoto)
    templabel.image = tempphoto
    templabel.grid(column=0, row=0, sticky=("W, E"))
    tempnowphoto = getimage("/var/www/reports/tempnow.png")
    tempnowlabel = ttk.Label(tempReport, image=tempnowphoto)
    tempnowlabel.image = tempnowphoto
    tempnowlabel.grid(column=0, row=1, sticky=("W, E"))

    windReport = ttk.Labelframe(tab3, text="Wind", style="BM.TLabelframe")
    windReport.grid(column=2, row=1, sticky=("N"))               
    windphoto = getimage("/var/www/reports/wind.png")
    windlabel = ttk.Label(windReport, image=windphoto)
    windlabel.image = windphoto
    windlabel.grid(column=0, row=0, sticky=("W, E"))    
    windnowphoto = getimage("/var/www/reports/windnow.png")
    windnowlabel = ttk.Label(windReport, image=windnowphoto)
    windnowlabel.image = windnowphoto
    windnowlabel.grid(column=0, row=1, sticky=("W, E"))
    
    solarReport = ttk.Labelframe(tab3, text="Solar", style="BM.TLabelframe")
    solarReport.grid(column=3, row=1, sticky=("N"))               
    solarphoto = getimage("/var/www/reports/solar.png")
    solarlabel = ttk.Label(solarReport, image=solarphoto)
    solarlabel.image = solarphoto
    solarlabel.grid(column=0, row=0, sticky=("W, E"))
    solarnowphoto = getimage("/var/www/reports/solarnow.png")
    solarnowlabel = ttk.Label(solarReport, image=solarnowphoto)
    solarnowlabel.image = solarnowphoto
    solarnowlabel.grid(column=0, row=1, sticky=("W, E"))
    
    pressReport = ttk.Labelframe(tab3, text="Pressure", style="BM.TLabelframe")
    pressReport.grid(column=4, row=1, sticky=("N"))               
    pressphoto = getimage("/var/www/reports/pressure.png")
    presslabel = ttk.Label(pressReport, image=pressphoto)
    presslabel.image = pressphoto
    presslabel.grid(column=0, row=0, sticky=("W, E"))
    pressnowphoto = getimage("/var/www/reports/pressurenow.png")
    pressnowlabel = ttk.Label(pressReport, image=pressnowphoto)
    pressnowlabel.image = pressnowphoto
    pressnowlabel.grid(column=0, row=1, sticky=("W, E"))

def dovolts(*args):
    voltReport = ttk.Labelframe(tab1, text="Board Charts", style="BM.TLabelframe")
    voltReport.grid(column=3, row=9, sticky=("N"))   
    voltphoto = getimage("/var/www/reports/bvolts.png")
    voltlabel = ttk.Label(voltReport, image=voltphoto)
    voltlabel.image = voltphoto
    voltlabel.grid(column=0, row=0, sticky=("W, E"))
    btempphoto = getimage("/var/www/reports/btemp.png")
    btemplabel = ttk.Label(voltReport, image=btempphoto)
    btemplabel.image = btempphoto
    btemplabel.grid(column=1, row=0, sticky=("W, E"))
    root.after(1000 * 60 * 10, dovolts)    ## 10  minutes 
    
def getimage(fname):
    try:
        tempimage = Image.open("/var/www/img/na.gif")
        temp = tempimage.resize((300, 300),Image.ANTIALIAS)
        img = ImageTk.PhotoImage(temp)
        db = mdb.connect(host= server.get(), port = eoss.SQL.port, user= eoss.SQL.user,passwd= eoss.SQL.password, db= eoss.SQL.database)
        cur = db.cursor(mdb.cursors.DictCursor)
        tnow = datetime.now()
        
        try:
            sql = "Select IMG from CORE_IMG where FILENAME = '" + fname + "' and We_Date = '" + tnow.strftime("%y-%m-%d") + "' limit 0,1"
            cur.execute(sql)
            db.commit()
            row = cur.fetchone()
            if row is not None:
                filelike = cS.StringIO(row["IMG"])
                tempimage = Image.open(filelike)
                temp = tempimage.resize((300, 300),Image.ANTIALIAS)
                img = ImageTk.PhotoImage(temp)
        except:
            pass
        cur.close()
        db.close()
    except:
        pass
    return img
def geticon(fname):
    tempimage = Image.open(fname)
    temp = tempimage.resize((50, 50),Image.ANTIALIAS)
    return ImageTk.PhotoImage(temp)

def getweather(*args):
    strError.set("")
    try:
        
        db = mdb.connect(host= server.get(), port = eoss.SQL.port, user= eoss.SQL.user,passwd= eoss.SQL.password, db= eoss.SQL.database)
        cur = db.cursor(mdb.cursors.DictCursor)
        
        try:

            strError.set(eosu.getsetting(db, "NAME", 0))    
            eor_version.set(eosu.getsetting(db, "EOR_VERSION", 0))
            eos_version.set(eosu.getsetting(db, "EOS_VERSION", 0))
            cur.execute("SELECT * FROM BOARD order by W_TIME desc limit 0,1")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                 version.set(row["VERSION"])
                 battery.set("{0:.1f} V ".format(row["B_VOLTAGE"]))
                 source.set("{0:.1f} V ".format(row["S_VOLTAGE"]))
                 cabTemp.set("{0:.1f} C ".format(row["C_TEMP"]))
            else:
                version.set("N/A")

            cur.execute("SELECT INT_VALUE as I, STR_VALUE as F FROM STATION where LABEL ='HAS_FAN'")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                if row["I"] > 0:
                    fanState.set(row["F"])
                else:
                    fanState.set("Not Enabled")
            else:
                fanState.set("")
                

            cur.execute("SELECT COUNT(W_TIME) as C FROM FEED")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                feedCount.set(row["C"])
            else:
                feedCount.set("N/A")

            cur.execute("SELECT W_TIME FROM FEED order by W_TIME desc limit 0,1")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                feedTime.set(row["W_TIME"])
            
            cur.execute("SELECT WE_DATE_TIME FROM CORE_DATA order by WE_DATE_TIME desc limit 0,1")
            db.commit()
            row = cur.fetchone()
            if row is not None:
                archived.set(row["WE_DATE_TIME"])            
                
            if eosu.getsetting(db, "TEMP_COUNT", 1) > 0:
                try:
                    a = "SELECT * FROM FEED WHERE TYPE = 3 order by W_TIME desc limit 0,1"                
                    cur.execute(a)
                    db.commit()
                    row = cur.fetchone()
                

                    if row is not None:
                        out = round(float(row["B1"]) + (float(row["B2"])/ 10),1)
                        dew = round(float(row["B3"]) + (float(row["B4"])/ 10),1)
                        rel = float(row["B5"])
                        if float(row["B6"]) == 1:
                            out = out * -1
                        if float(row["B7"]) == 1:
                            dew = dew * -1
                        t_dew.set("{0:.1f} C ".format(dew))
                        t_max.set("{0:.1f} C ".format(out))
                        t_hum.set("{0:.1f} %".format(rel))

                except:
                    pass
                if eosu.getsetting(db, "PRESSURE_COUNT", 1) > 0:

                    try: 
                        a = "SELECT * FROM FEED WHERE TYPE = 2 order by W_TIME desc limit 0,1"        
                        cur.execute(a)
                        db.commit()
                        row = cur.fetchone()
                        if row is not None: 
                            pabs = float(int(row["B2"]) + (256 * int(row["B1"])))/100
                            alt = float(int(row["B3"]) + (256 * int(row["B4"])))
                            prel = float(int(row["B6"]) + (256 * int(row["B5"])))/100
                            ptrend = float(int(row["B7"]))
                            ##Deterime if preassure is rising then add 5
                            if float(int(row["B8"]))== 1 and float(int(row["B7"])) > 0:
                                ptrend = float(int(row["B7"]))+ 5
                            
                            p_avg.set("{0:.1f} kPa".format(pabs))
                    except:
                        pass
                if eosu.getsetting(db, "SOLAR_COUNT", 1) > 0:

                    try:
                        a = "SELECT * FROM FEED WHERE TYPE = 5 order by W_TIME desc limit 0,1"
                        cur.execute(a)
                        db.commit()
                        row = cur.fetchone()
                        if row is not None:     
                            lum = float(int(row["B2"]) + (256 * int(row["B1"])))
                            uv = float(row["B3"])
                            rad = float(int(row["B5"]) + (256 * int(row["B4"])))
                            if rad == 0:
                                rad = round(lum * .0079,3)
                            if lum == 0:
                                lum = round(rad * 126.58,0)
                            
                            
                                                              
                            sr_avg.set("{0:.1f} W/m2".format(rad))
                            sr_uv.set("{0:.1f}".format(uv))

                        a = "SELECT SOLAR_ENERGY as E FROM CORE_DATE where WE_DATE > DATE_SUB(sysdate(),INTERVAL 1 DAY)"
                        cur.execute(a)
                        db.commit()
                        row = cur.fetchone()
                        if row is not None:     
                            eng = row["E"]
                            sr_eng.set(eng + " Ly")
                        a = "SELECT CAST(SUN_HRS as DECIMAL(10,1)) as S FROM CORE_DATE where WE_DATE > DATE_SUB(sysdate(),INTERVAL 1 DAY)"
                        cur.execute(a)
                        db.commit()
                        row = cur.fetchone()
                        if row is not None:     
                            eng = row["S"]
                            sr_hrs.set("{0:.1f} today".format(eng))                        

                            
                    except:
                        pass

                if eosu.getsetting(db, "WIND_COUNT", 1) > 0:
                    try:       
                        a = "SELECT * FROM FEED WHERE TYPE = 1 order by W_TIME desc limit 0,1"                                  
                        cur.execute(a)
                        db.commit()
                        row = cur.fetchone()
                        if row is not None:                                
                            spd = round(float(row["B1"]) + (float(row["B2"]) /10),1)
                            #gust = round(float(row["B3"]) + (float(row["B4"]) /10),1)
                            #avgspd = round(float(row["B5"]) + (float(row["B6"]) /10),1)                           
                            wdir = float(row["B8"] + row["B9"])
                            if spd > 0:
                                w_rose = eosu.wind.windrose(wdir)
                            else:
                                w_rose = "---"                                                

                            w_dir.set(w_rose)
                            w_spd.set("{0:.1f} Kph".format(spd))

                        a = "SELECT  ROUND(MAX(SPEED),0) as GUST, ROUND(AVG(SPEED),0) as AVS, ROUND(AVG(SPEED)* .539957,1) AS KNOTS FROM WIND where W_TIME > DATE_SUB(sysdate(),INTERVAL 10 MINUTE)"
                        cur.execute(a)
                        db.commit()
                        row = cur.fetchone()
                        if row is not None:
                            w_10min.set("{0:.1f} Kph".format(row["AVS"]))
                            w_gust.set("{0:.1f} Kph".format(row["GUST"]))
                    except:
                        pass

                if eosu.getsetting(db, "RAIN_COUNT", 1) > 0:
                    try:
                        a = "SELECT ROUND(AVG(RATE),1) AS RR, ROUND(MAX(RAIN_AMOUNT),1)as R, ROUND(MAX(TIPS),0) as T, ROUND(MAX(FALL_TODAY),2) as FT, ROUND(MAX(FALL_YESTERDAY),2) as FY  FROM RAIN WHERE  W_TIME > DATE_SUB(sysdate(),INTERVAL 10 MINUTE)  order by W_TIME desc limit 0,1"
                        cur.execute(a)
                        db.commit()
                        row = cur.fetchone()
                        if row is not None:
                            if row["RR"] > 0:
                                r_rate.set("{0:.1f} mm".format(row["RR"]))
                            else:
                                r_rate.set("")
                            if row["FT"] > 0:
                                r_today.set("{0:.1f} mm".format(row["FT"]))
                            else:
                                r_today.set("")
                            if row["FY"] > 0:
                                r_yest.set("{0:.1f} mm".format(row["FY"]))
                            else:
                                r_yest.set("")
                            if row["T"] > 0:
                                r_tips.set("{0:.0f}".format(row["T"]))
                            else:
                                r_tips.set("")
                        a = "SELECT ROUND(SUM(CAST(RAIN as DECIMAL(10,2))),1) as RAIN FROM CORE_DATE where WE_DATE > DATE_SUB(sysdate(),INTERVAL 7 DAY)"
                        cur.execute(a)
                        db.commit()
                        row = cur.fetchone()
                        if row is not None:
                            r_7days.set("{0:.1f} mm".format(row["RAIN"]))
                        a = "SELECT ROUND(SUM(CAST(RAIN as DECIMAL(10,2))),1) as RAIN FROM CORE_DATE where WE_DATE > DATE_SUB(sysdate(),INTERVAL 30 DAY)"
                        cur.execute(a)
                        db.commit()
                        row = cur.fetchone()
                        if row is not None:
                            r_30days.set("{0:.1f} mm".format(row["RAIN"]))

                    except:
                        pass
                root.after(10000, getweather)
                
                                
        except:
            pass
    


    except :
        strError.set("No Connection")
        t_dew.set("")
        t_max.set("")
        t_hum.set("")
        p_avg.set("")
        sr_avg.set("")
        sr_uv.set("")
        sr_eng.set("")
        sr_hrs.set("")
        w_spd.set("")
        w_dir.set("")
        w_10min.set("")
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
            

root = tk.Tk()
root.configure(background="white")
root.title("EOS Weather")


mainframe = tk.Frame(root)
mainframe.configure(background="white")
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

img1 = geticon("/var/www/img/weather256.png")
img2 = geticon("/var/www/img/wind_flag_storm.png")
img3 = geticon("/var/www/img/line_chart.png")
img4 = geticon("/var/www/img/xml.png")
img5 = geticon("/var/www/img/good.png")

n.add(tab1, text='Station', image = img1, compound='top')
n.add(tab2, text='Instruments', image = img2, compound='top')
n.add(tab3, text ='Charts', image = img3, compound='top')
n.add(tab4, text = 'Reports', image = img4, compound='top')
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
r_7days = tk.StringVar()
r_30days = tk.StringVar()

reportval = tk.StringVar()
tableval = tk.StringVar()

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

## Configure styles
moduleStyle = ttk.Style()
moduleStyle.configure("BM.TFrame", foreground="black", background="white")
moduleStyle.configure("BM.TLabelframe", foreground="black", background="white")
moduleStyle.configure("BM.TLabelframe.Label", foreground="black", background="white", font=("helvetica", 16))
moduleStyle.configure("BM.TCombobox.Listbox", foreground="black", background="white", font=("helvetica", 16))
moduleStyle.configure("BM.TLabel", foreground="gray", background="white" , font=("helvetica", 10))
moduleStyle.configure("M.TLabel", foreground="black", background="white" , font=("helvetica", 20))
moduleStyle.configure("M1.TLabel", foreground="gray", background="white" , font=("helvetica", 20))
moduleStyle.configure("M3.TLabel", foreground="gray", background="lavender" , font=("helvetica", 20))
moduleStyle.configure("M2.TLabel", foreground="black", background="lavender" , font=("helvetica", 20))
moduleStyle.configure("TM.TLabel", foreground="red", background="white" , font=("helvetica", 40))
moduleStyle.configure("SM.TLabelframe", foreground="black", background="white")
moduleStyle.configure("SM.TLabelframe.Label", foreground="black", background="white", font=("helvetica", 16))
moduleStyle.configure("SM.TLabel", foreground="blue", background="yellow" , font=("helvetica", 40))
moduleStyle.configure("WM.TLabelframe", foreground="black", background="white")
moduleStyle.configure("WM.TLabel", foreground="blue", background="white" , font=("helvetica", 40))
moduleStyle.configure("WM.TLabelframe.Label", foreground="black", background="white", font=("helvetica", 16))
moduleStyle.configure("RM.TLabelframe", foreground="black", background="white")
moduleStyle.configure("RM.TLabelframe.Label", foreground="black", background="white", font=("helvetica", 16))
moduleStyle.configure("RM.TLabel", foreground="white", background="blue" , font=("helvetica", 40))
bigfont = tkf.Font(family='helvetica',size=20)
root.option_add('*TCombobox*Listbox*Font',bigfont)


## icons
logonicon = geticon("/var/www/img/graph.png")
boardicon = geticon("/var/www/img/no_network.png")
upicon = geticon("/var/www/img/arrow_up.png")
downicon = geticon("/var/www/img/arrow_down.png")
exiticon = geticon("/var/www/img/down.png")

## Buttons
ttk.Button(tab1, text="Connect", image=logonicon, command=getweather, compound="bottom").grid(column=0, row=0, sticky="W")
ttk.Button(tab1, text="Exit", command=quit, image=exiticon, compound="top").grid(column=0, row=10, sticky="S, W")
ttk.Button(tab1, text="Get Board Charts", command=dovolts, image=boardicon, compound="bottom").grid(column=0, row=9, sticky="W")
ttk.Button(tab3, text="Get Charts", command=docharts, image=downicon, compound="top").grid(column=0, row=0, sticky="W")
ttk.Button(tab4, text="Get NOAA Report", command=donoaareport, image=downicon, compound="top").grid(column=1, row=0, sticky="W")
ttk.Button(tab4, text="Get Source Table", command=dotable, image=upicon, compound="bottom").grid(column=0, row=0, sticky="W")
ttk.Button(tab5, text="Get Summary", command=dosummary, image=downicon, compound="top").grid(column=0, row=0, sticky="W")


## Lists
reportlist = ttk.Combobox(tab4, textvariable=reportval, font=bigfont, state='readonly')
reportlist['values'] = ('NOAA Month','NOAA Previous Month','NOAA Year','NOAA Previous Year')
reportlist.current(0)
reportlist.grid(column=1, row=1, sticky="W, N")

tablelist = ttk.Combobox(tab4, textvariable=tableval, font=bigfont, state='readonly')
tablelist['values'] = ('Alarm','Almanac','Archive','Board','Date','Depth','Feed','Pressure','Rain','Relay','Soil','Solar','Temp','Wind')
tablelist.current(0)
tablelist.grid(column=0, row=1, sticky="W, N")

##Labels
strError.set("IP Address of Station")
ttk.Label(tab1, textvariable=strError, style="M.TLabel").grid(column=3, row=0, sticky=("W, E"))

## Tab 1 Station

server_entry = ttk.Entry(tab1, width=20, textvariable=server, font=bigfont)
server.set(eoss.SQL.server)
server_entry.grid(column=1, row=0, sticky=("W, E"))


Modules = ttk.Labelframe(tab1, text='Modules', style="BM.TLabelframe")
Modules.grid(column=0, row=1, sticky=("N"))

ttk.Label(Modules, text="Firmware Version : ", style="BM.TLabel").grid(column=0, row=2, sticky="E")
ttk.Label(Modules, textvariable=version, style="M.TLabel").grid(column=1, row=2, sticky=("W, E"))
ttk.Label(Modules, text="Eos Version : ", style="BM.TLabel").grid(column=0, row=3, sticky="E")
ttk.Label(Modules, textvariable=eos_version, style="M.TLabel").grid(column=1, row=3, sticky=("W, E"))
ttk.Label(Modules, text="Eos Version : ", style="BM.TLabel").grid(column=0, row=4, sticky="E")
ttk.Label(Modules, textvariable=eos_version, style="M.TLabel").grid(column=1, row=4, sticky=("W, E"))


stationModule = ttk.Labelframe(tab1, text='Station Status', style="BM.TLabelframe")
stationModule.grid(column=1, row=1, sticky=("N"))
ttk.Label(stationModule, text="Fan State : ", style="BM.TLabel").grid(column=0, row=1, sticky="E")
ttk.Label(stationModule, textvariable=fanState, style="M.TLabel").grid(column=1, row=1, sticky=("W, E"))
ttk.Label(stationModule, text="Cabinet Temp : ", style="BM.TLabel").grid(column=0, row=2, sticky="E")
ttk.Label(stationModule, textvariable=cabTemp, style="M.TLabel").grid(column=1, row=2, sticky=("W, E"))
ttk.Label(stationModule, text="Battery : ", style="BM.TLabel").grid(column=0, row=3, sticky="E")
ttk.Label(stationModule, textvariable=battery, style="M.TLabel").grid(column=1, row=3, sticky=("W, E"))
ttk.Label(stationModule, text="Source : ", style="BM.TLabel").grid(column=0, row=4, sticky="E")
ttk.Label(stationModule, textvariable=source, style="M.TLabel").grid(column=1, row=4, sticky=("W, E"))
ttk.Label(stationModule, text="Feed Count : ", style="BM.TLabel").grid(column=0, row=5, sticky="E")
ttk.Label(stationModule, textvariable=feedCount, style="M.TLabel").grid(column=1, row=5, sticky=("W, E"))
ttk.Label(stationModule, text="Feed Time : ", style="BM.TLabel").grid(column=0, row=6, sticky="E")
ttk.Label(stationModule, textvariable=feedTime, style="M.TLabel").grid(column=1, row=6, sticky=("W, E"))
ttk.Label(stationModule, text="Archived : ", style="BM.TLabel").grid(column=0, row=7, sticky="E")
ttk.Label(stationModule, textvariable=archived, style="M.TLabel").grid(column=1, row=7, sticky=("W, E"))

## Tab 2  Instuments
baseModule = ttk.Labelframe(tab2, text='Base Module', style="BM.TLabelframe")
baseModule.grid(column=0, row=0, sticky=("N"))
ttk.Label(baseModule, text='TMP : ', style="BM.TLabel").grid(column=0, row=1, sticky=("E"))
ttk.Label(baseModule, textvariable=t_max, style="TM.TLabel").grid(column=1, row=1, sticky=("W"))
ttk.Label(baseModule, text='DEW : ', style="BM.TLabel").grid(column=0, row=2, sticky=("E"))
ttk.Label(baseModule, textvariable=t_dew, style="TM.TLabel").grid(column=1, row=2, sticky=("W"))
ttk.Label(baseModule, text='HUM : ', style="BM.TLabel").grid(column=0, row=3, sticky=("E"))
ttk.Label(baseModule, textvariable=t_hum, style="TM.TLabel").grid(column=1, row=3, sticky=("W"))
ttk.Label(baseModule, text='PRE : ', style="BM.TLabel").grid(column=0, row=4, sticky=("E"))
ttk.Label(baseModule, textvariable=p_avg, style="TM.TLabel").grid(column=1, row=4, sticky=("W"))

solarModule = ttk.Labelframe(tab2, text='Solar Module', style="SM.TLabelframe")
solarModule.grid(column=2, row=0, sticky=("N"))
ttk.Label(solarModule, text='RAD : ', style="BM.TLabel").grid(column=0, row=1, sticky=("E"))
ttk.Label(solarModule, textvariable=sr_avg, style="SM.TLabel").grid(column=1, row=1, sticky=("E,W"))
ttk.Label(solarModule, text='UV : ', style="BM.TLabel").grid(column=0, row=2, sticky=("E"))
ttk.Label(solarModule, textvariable=sr_uv, style="SM.TLabel").grid(column=1, row=2, sticky=("E,W"))
ttk.Label(solarModule, text='ENG : ', style="BM.TLabel").grid(column=0, row=3, sticky=("E"))
ttk.Label(solarModule, textvariable=sr_eng, style="SM.TLabel").grid(column=1, row=3, sticky=("E,W"))
ttk.Label(solarModule, text='HRS : ', style="BM.TLabel").grid(column=0, row=4, sticky=("E"))
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
ttk.Label(windModule, textvariable=w_gust, style="WM.TLabel").grid(column=1, row=4, sticky=("W, E"))

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
ttk.Label(rainModule, text='7 DAY : ', style="BM.TLabel").grid(column=0, row=5, sticky=("E"))
ttk.Label(rainModule, textvariable=r_7days, style="RM.TLabel").grid(column=1, row=5, sticky=("W, E"))
ttk.Label(rainModule, text='30 DAY : ', style="BM.TLabel").grid(column=0, row=6, sticky=("E"))
ttk.Label(rainModule, textvariable=r_30days, style="RM.TLabel").grid(column=1, row=6, sticky=("W, E"))

## Tab 3 Charts

## Tab 4 Reports

## Tab 5 Summary

dailyLabel = ttk.Labelframe(tab5, text="Reading", style="BM.TLabelframe")
dailyLabel.grid(column=0, row=1, sticky=("N"))
ttk.Label(dailyLabel, text='Low Temp', style="M1.TLabel").grid(column=0, row=1, sticky=("E,W"))
ttk.Label(dailyLabel, text='High Temp', style="M3.TLabel").grid(column=0, row=2, sticky=("E,W"))
ttk.Label(dailyLabel, text='Low Pressure', style="M1.TLabel").grid(column=0, row=3, sticky=("E,W"))
ttk.Label(dailyLabel, text='High Pressure', style="M3.TLabel").grid(column=0, row=4, sticky=("E,W"))
ttk.Label(dailyLabel, text='Average Wind', style="M1.TLabel").grid(column=0, row=5, sticky=("E,W"))
ttk.Label(dailyLabel, text='Hi Wind', style="M3.TLabel").grid(column=0, row=6, sticky=("E,W"))
ttk.Label(dailyLabel, text='Wind Run', style="M1.TLabel").grid(column=0, row=7, sticky=("E,W"))
ttk.Label(dailyLabel, text='Sunlight', style="M3.TLabel").grid(column=0, row=8, sticky=("E,W"))

dailyReport = ttk.Labelframe(tab5, text="Today", style="BM.TLabelframe")
dailyReport.grid(column=1, row=1, sticky=("N"))
ttk.Label(dailyReport, textvariable=d_lowTemp, style="M.TLabel").grid(column=1, row=1, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=d_hiTemp, style="M2.TLabel").grid(column=1, row=2, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=d_lowPress, style="M.TLabel").grid(column=1, row=3, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=d_hiPress, style="M2.TLabel").grid(column=1, row=4, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=d_avgWind, style="M.TLabel").grid(column=1, row=5, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=d_hiWind, style="M2.TLabel").grid(column=1, row=6, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=d_runWind, style="M.TLabel").grid(column=1, row=7, sticky=("W, E"))
ttk.Label(dailyReport, textvariable=d_sun, style="M2.TLabel").grid(column=1, row=8, sticky=("W, E"))

weekReport = ttk.Labelframe(tab5, text="7 days", style="BM.TLabelframe")
weekReport.grid(column=2, row=1, sticky=("N"))
ttk.Label(weekReport, textvariable=w_lowTemp, style="M.TLabel").grid(column=1, row=1, sticky=("W, E"))
ttk.Label(weekReport, textvariable=w_hiTemp, style="M2.TLabel").grid(column=1, row=2, sticky=("W, E"))
ttk.Label(weekReport, textvariable=w_lowPress, style="M.TLabel").grid(column=1, row=3, sticky=("W, E"))
ttk.Label(weekReport, textvariable=w_hiPress, style="M2.TLabel").grid(column=1, row=4, sticky=("W, E"))
ttk.Label(weekReport, textvariable=w_avgWind, style="M.TLabel").grid(column=1, row=5, sticky=("W, E"))
ttk.Label(weekReport, textvariable=w_hiWind, style="M2.TLabel").grid(column=1, row=6, sticky=("W, E"))
ttk.Label(weekReport, text= "", style="M1.TLabel").grid(column=1, row=7, sticky=("W, E"))
ttk.Label(weekReport, textvariable=w_sun, style="M2.TLabel").grid(column=1, row=8, sticky=("W, E"))

weekDateReport = ttk.Labelframe(tab5, text="on", style="BM.TLabelframe")
weekDateReport.grid(column=3, row=1, sticky=("N"))
ttk.Label(weekDateReport, textvariable=wd_lowTemp, style="M1.TLabel").grid(column=1, row=1, sticky=("W, E"))
ttk.Label(weekDateReport, textvariable=wd_hiTemp, style="M3.TLabel").grid(column=1, row=2, sticky=("W, E"))
ttk.Label(weekDateReport, textvariable=wd_lowPress, style="M1.TLabel").grid(column=1, row=3, sticky=("W, E"))
ttk.Label(weekDateReport, textvariable=wd_hiPress, style="M3.TLabel").grid(column=1, row=4, sticky=("W, E"))
ttk.Label(weekDateReport, text="", style="M1.TLabel").grid(column=1, row=5, sticky=("W, E"))
ttk.Label(weekDateReport, textvariable=wd_hiWind, style="M3.TLabel").grid(column=1, row=6, sticky=("W, E"))
ttk.Label(weekDateReport, text= "", style="M1.TLabel").grid(column=1, row=7, sticky=("W, E"))
ttk.Label(weekDateReport, textvariable=wd_sun, style="M3.TLabel").grid(column=1, row=8, sticky=("W, E"))

monthReport = ttk.Labelframe(tab5, text="30 days", style="BM.TLabelframe")
monthReport.grid(column=4, row=1, sticky=("N"))
ttk.Label(monthReport, textvariable=m_lowTemp, style="M.TLabel").grid(column=1, row=1, sticky=("W, E"))
ttk.Label(monthReport, textvariable=m_hiTemp, style="M2.TLabel").grid(column=1, row=2, sticky=("W, E"))
ttk.Label(monthReport, textvariable=m_lowPress, style="M.TLabel").grid(column=1, row=3, sticky=("W, E"))
ttk.Label(monthReport, textvariable=m_hiPress, style="M2.TLabel").grid(column=1, row=4, sticky=("W, E"))
ttk.Label(monthReport, textvariable=m_avgWind, style="M.TLabel").grid(column=1, row=5, sticky=("W, E"))
ttk.Label(monthReport, textvariable=m_hiWind, style="M2.TLabel").grid(column=1, row=6, sticky=("W, E"))
ttk.Label(monthReport, text="", style="M.TLabel").grid(column=1, row=7, sticky=("W, E"))
ttk.Label(monthReport, textvariable=m_sun, style="M2.TLabel").grid(column=1, row=8, sticky=("W, E"))

monthDateReport = ttk.Labelframe(tab5, text="on", style="BM.TLabelframe")
monthDateReport.grid(column=5, row=1, sticky=("N"))
ttk.Label(monthDateReport, textvariable=md_lowTemp, style="M1.TLabel").grid(column=1, row=1, sticky=("W, E"))
ttk.Label(monthDateReport, textvariable=md_hiTemp, style="M3.TLabel").grid(column=1, row=2, sticky=("W, E"))
ttk.Label(monthDateReport, textvariable=md_lowPress, style="M1.TLabel").grid(column=1, row=3, sticky=("W, E"))
ttk.Label(monthDateReport, textvariable=md_hiPress, style="M3.TLabel").grid(column=1, row=4, sticky=("W, E"))
ttk.Label(monthDateReport, text="", style="M1.TLabel").grid(column=1, row=5, sticky=("W, E"))
ttk.Label(monthDateReport, textvariable=md_hiWind, style="M3.TLabel").grid(column=1, row=6, sticky=("W, E"))
ttk.Label(monthDateReport, text= "", style="M1.TLabel").grid(column=1, row=7, sticky=("W, E"))
ttk.Label(monthDateReport, textvariable=md_sun, style="M3.TLabel").grid(column=1, row=8, sticky=("W, E"))


## Clean UP and set window size
for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

server_entry.focus()
root.bind('<Return>', getweather)
##root.attributes('-fullscreen', True)
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w,h))
## RUN
root.mainloop()
