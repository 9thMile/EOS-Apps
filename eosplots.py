#!/usr/bin/env python
import sys
import subprocess
from time import sleep
from datetime import date, datetime, time, timedelta, tzinfo
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import eossql as eoss
import eospush as eosp
import eosutils as eosu
import MySQLdb as mdb
from operator import sub
import logging
import logging.handlers

LOG_FILENAME = '/var/www/logs/plot.log'
has_db = False
t = []
ws = []
wh = []
d = []
bar = []
rad = []
smax = []
t1 = []
ws1 = []
wh1 = []
d1 = []
bar1 = []
rad1 = []
smax1 = []
d3 = []
bt = []
ct = []
vb = []
vs = []
dd = []
dd1 = []
dt = []
dt1 = []
da = []
dh = []
dh1 = []
sd = []
sd1 = []
st = []
st1 = []
sm = []
sm1 = []
aTimer = 90 ##90
bTimer = 300 ##300

class Station:
    Has_Wind = 0
    Has_Temp = 0
    Has_Rain = 0
    Has_Pressure = 0
    Has_Board = 0
    Has_Soil = 0
    Has_Depth = 0
    Datum = 0
    HHWL = 0
    Has_Solar = 0
    Remote_ID = ""
    Remote_Conn = ""
    Burst_USN = ""
    Burst_PWD = ""
    Has_Burst = False
    Has_Core = 0
    Has_Cam = False
    WebCam = ""
    

def getstation(Station, db):
    Station.HasCam = False
    Station.HasBurst = False
    Station.Has_Wind = eosu.getsetting(db, "WIND_COUNT", 1)
    Station.Has_Temp = eosu.getsetting(db, "TEMP_COUNT", 1)
    Station.Has_Rain = eosu.getsetting(db, "RAIN_COUNT", 1)
    Station.Has_Pressure = eosu.getsetting(db, "PRESSURE_COUNT", 1)
    Station.Has_Board = eosu.getsetting(db, "BOARD_COUNT", 1)
    Station.Has_Soil = eosu.getsetting(db, "SOIL_COUNT", 1)
    Station.Has_Depth = eosu.getsetting(db, "DEPTH_COUNT", 1)
    Station.HHWL = eosu.getsetting(db, "DEPTH_HHWL", 1)
    Station.Datum = eosu.getsetting(db, "DEPTH_COUNT", 2)
    Station.Has_Solar = eosu.getsetting(db, "SOLAR_COUNT", 1)
    Station.Remote_ID = eosu.getsetting(db, "Rem_ID", 0)
    if len(Station.Remote_ID) > 1:
        Station.Remote_Conn  = eosu.getsetting(db, "REM_CONN", 0)
        Station.Burst_USN  = eosu.getsetting(db, "BURST_USN", 0)
        Station.Burst_PWD  = eosu.getsetting(db, "BURST_PWD", 0)
        Station.WebCam = eosu.getsetting(db, "W_UNDER_CAMFILE", 0)        
        if eosu.getsetting(db,"REM_BURST",1) == 1:
            Station.Has_Burst = True
        if len(Station.WebCam) > 1:
            Station.HasCam = True
    Station.Has_Core = Station.Has_Temp + Station.Has_Pressure + Station.Has_Wind + Station.Has_Solar

def burstCam(Station):   
    CamFiles = Station.WebCam.split('/')
    CamFile = CamFiles[len(CamFiles)-1]
    
    sent,reason = eosp.burstupload(Station, "/" + CamFile, Station.WebCam)

def savetodb(f_name, tnow, db):
    try:
        cur = db.cursor(mdb.cursors.DictCursor)
        image = open(f_name,'rb').read()
        sql = "DELETE FROM CORE_IMG where FILENAME ='" + f_name + "'"
        cur.execute(sql)
        db.commit()
        sql = "INSERT CORE_IMG (We_Date, FILENAME) VALUES('" + tnow.strftime("%Y-%m-%d") + "', '" + f_name + "')"
        cur.execute(sql)
        db.commit()
        sql = "UPDATE CORE_IMG SET IMG = '" + db.escape_string(image) + "' where FILENAME ='" + f_name + "' and We_Date ='" + tnow.strftime("%Y-%m-%d") + "'"
        cur.execute(sql)
        db.commit()
        cur.close()
        return True
    except:
        return False
        
def reset():
    del t[:]
    del ws[:]
    del wh[:]
    del d[:]
    del bar[:]
    del rad[:]
    del smax[:]
    del t1[:]
    del ws1[:]
    del wh1[:]
    del d1[:]
    del bar1[:]
    del rad1[:]
    del smax1[:]
    del d3[:]
    del bt[:]
    del ct[:]
    del vb[:]
    del vs[:]
    del dd[:]
    del dd1[:]
    del dt[:]
    del dt1[:]
    del da[:]
    del dh[:]
    del dh1[:]
    del sd[:]
    del sd1[:]
    del st[:]
    del st1[:]
    del sm[:]
    del sm1[:]
    
def main():
    ##wait for system to start
    
    time.sleep(aTimer)
    """Set up logging files """
    eosu.log.clear(LOG_FILENAME)
    level = logging.INFO ##Change this to modify logging details for all messages DEBUG/INFO
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(lineno)d -> %(message)s")
    
    if len(sys.argv) > 1:
        level_name = sys.argv[1]
        level = eosu.log.LEVELS.get(level_name, logging.NOTSET)

    logging.basicConfig(filename=LOG_FILENAME,level=level) 
    plot_log = logging.getLogger('eosLogger')
    if level == logging.DEBUG:
        handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=100000, backupCount=10)
    else:
        handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=20000, backupCount=10)
    
    handler.setFormatter(formatter)
    plot_log.addHandler(handler)
    try:
            
        db = mdb.connect(host= eoss.SQL.server, port = eoss.SQL.port, user= eoss.SQL.user,passwd= eoss.SQL.password, db= eoss.SQL.database)
        cur = db.cursor(mdb.cursors.DictCursor)
        has_db = True
        plot_log.info('Connected database')
    except:
        plot_log.critical('No database connection')
##        if len(Station.User_Key) > 0:
##             eosp.sendpushover(Station.App_Token, Station.User_Key, "Plot Server NOT Starting: No database", 1)
        has_db = False        
    try:
        while has_db == True:
            plot_log.info('STARTING CYCLE')
            reset()
            tnow = datetime.now()
            dnow = tnow - timedelta(days=7)
            d1now = tnow - timedelta(days=1)
            getstation(Station, db)
            if Station.HasCam == True:
                burstCam(Station)


            if Station.Has_Depth > 0:
                plot_log.info('Depth Starting...')
                try:

                    query = "Select DEPTH_ID from DEPTH group by DEPTH_ID"
                    cur.execute(query)
                    soils = cur.fetchall()
                    for soil in soils:
                        sid = soil["DEPTH_ID"]
                        plot_log.info('Depth ID :' + str(sid))
                        query = "Select * from DEPTH where DEPTH_ID = " + str(sid)
                        cur.execute(query)
                        result = cur.fetchall()    
                        for record in result:
                            a = record["W_TIME"]
                            dd1.append(a)
                            dh1.append(Station.HHWL)
                            if record["DEPTH"] == '---':
                                dt1.append(0)
                            else:
                                dt1.append( float(record["DEPTH"]))

                        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
                        plt.gca().xaxis.set_major_locator(mdates.HourLocator())
                        lines = plt.plot_date(dd1,dt1,'r-',xdate=True, ydate=False)
                        lines = plt.plot_date(dd1,dh1,'y--',xdate=True, ydate=False)
                        ##plt.setp(lines,color='b', linewidth=3)
                        plt.title('Tide Detail (24hrs) #' + str(sid))
                        plt.xlabel('Hour')
                        plt.ylabel('cm')
                        plt.grid(True)
                        plot_log.info('Depth saving')
                        f_name = '/var/www/reports/detaildepth' + str(sid) + '.png'
                        plt.savefig(f_name)
                        if savetodb(f_name, tnow, db) == False:
                            plot_log.error("Plot not saved to DB : " + f_name)

                        plot_log.info('Depth finished')
    ##                    if Station.Has_Burst == True:
    ##                        sent,reason = eosp.burstupload(Station, "/detaildepth" + str(sid) + ".png", f_name)
                        #plt.show()
                        plt.cla()  #clears the axes
                except:
                    plot_log.error('Depth 24 hrs not ploted')
                time.sleep(aTimer)
                if Station.HasCam == True:
                    burstCam(Station)
                try:

                    plot_log.info('Depth Starting...')
                    query = "Select DEPTH_ID from DEPTH_DATA group by DEPTH_ID"
                    cur.execute(query)
                    soils = cur.fetchall()
                    for soil in soils:
                        sid = soil["DEPTH_ID"]
                        plot_log.info('Depth ID :' + str(sid))
                        query = "Select * from DEPTH_RISE_DATA where DEPTH_ID = " + str(sid) + " and WE_DATE_TIME > '" + dnow.isoformat() + "'"
                        cur.execute(query)
                        result = cur.fetchall()    
                        for record in result:
                            a = datetime.combine(record["WE_DATE"] , (datetime.min + record["WE_TIME"]).time())
                            dd.append(a)
                            dh.append(Station.HHWL/30.48)
                            if record["DEPTH"] == '---':
                                dt.append(0)
                            else:
                                dt.append(float(record["DEPTH"]))
                            if record["TIDE"] == '---':
                                da.append(0)
                            else:
                                da.append(float(record["TIDE"]))
                            
                        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
                        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
                        lines = plt.plot_date(dd,dt,'r-',xdate=True, ydate=False)    
                        lines = plt.plot_date(dd,da,'k_',xdate=True, ydate=False)
                        lines = plt.plot_date(dd,dh,'y--',xdate=True, ydate=False) 
                        ##plt.setp(lines,color='b', linewidth=3)
                        plt.title('Tide (7 Days) #' + str(sid))
                        plt.xlabel('Date (-- predicted)')
                        plt.ylabel('cm')
                        plt.grid(True)
                        plot_log.info('Depth saving')
                        f_name = '/var/www/reports/depth' + str(sid) + '.png'
                        plt.savefig(f_name)
                        if savetodb(f_name, tnow, db) == False:
                            plot_log.error("Plot not saved to DB : " + f_name)

                        plot_log.info('Depth finished')
                except:
                    plot_log.error('Depth 7 days period not ploted')
##                    if Station.Has_Burst == True:
##                        sent,reason = eosp.burstupload(Station, "/depth" + str(sid) + ".png", f_name)
                    #plt.show()
                plt.cla()  #clears the axes
                time.sleep(aTimer)
                if Station.HasCam == True:
                    burstCam(Station)

                
            if Station.Has_Core > 0:
                plot_log.info('Retrieving Core Data')
                try:
                    query = "Select * from CORE_DATA where WE_DATE_TIME > '" + dnow.isoformat() + "'"
                    cur.execute(query)
                    result = cur.fetchall()    
                    for record in result:
                        a = datetime.combine(record["WE_Date"] , (datetime.min + record["WE_Time"]).time())
                        d.append(a)
                        if record["TEMP_OUT"] == '---':
                            t.append(0)
                        else:
                            t.append(float(record["TEMP_OUT"]))
                        if record["WIND_SPEED"] == '---':
                            ws.append(0)
                        else:
                            ws.append(float(record["WIND_SPEED"]))
                        if record["WIND_HI"] == '---':
                            wh.append(0)
                        else:
                            wh.append(float(record["WIND_HI"]))
                        if record["BAR"] == '---':
                            bar.append(0)
                        else:
                            bar.append(float(record["BAR"])/10)
                        if record["SOLAR_RAD"] == '---':
                            rad.append(0)
                        else:
                            rad.append(float(record["SOLAR_RAD"]))
                        if record["SOLAR_MAX"] == '---':
                            smax.append(0)
                        else:
                            smax.append(float(record["SOLAR_MAX"]))

                    
                    query = "Select * from CORE_DATA where WE_DATE_TIME > '" + d1now.isoformat() + "'"
                    cur.execute(query)
                    result = cur.fetchall()
                    for record in result:
                        a = datetime.combine(record["WE_Date"] , (datetime.min + record["WE_Time"]).time())
                        d1.append(a)
                        if record["TEMP_OUT"] == '---':
                            t1.append(0)
                        else:
                            t1.append(float(record["TEMP_OUT"]))
                        if record["WIND_SPEED"] == '---':
                            ws1.append(0)
                        else:
                            ws1.append(float(record["WIND_SPEED"]))
                        if record["WIND_HI"] == '---':
                            wh1.append(0)
                        else:
                            wh1.append(float(record["WIND_HI"]))
                        if record["BAR"] == '---':
                            bar1.append(0)
                        else:
                            bar1.append(float(record["BAR"])/10)
                        if record["SOLAR_RAD"] == '---':
                            rad1.append(0)
                        else:
                            rad1.append(float(record["SOLAR_RAD"]))
                        if record["SOLAR_MAX"] == '---':
                            smax1.append(0)
                        else:
                            smax1.append(float(record["SOLAR_MAX"]))                    


                    if Station.Has_Temp > 0:
                        plot_log.info('Temp Starting...')
                        try:
                                
                            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
                            plt.gca().xaxis.set_major_locator(mdates.DayLocator())
                            lines = plt.plot_date(d,t,'-',xdate=True, ydate=False)

                            plt.setp(lines,color='r', linewidth=2)
                            plt.xlabel('Celsius')
                            plt.title('Temperature')
                            plt.grid(True)
                            plot_log.info('Temp saving weekly')
                            f1_name = "/var/www/reports/temp.png"
                            plt.savefig(f1_name)
                            if savetodb(f1_name, tnow, db) == False:
                                plot_log.error("Plot not saved to DB : " + f1_name)
                        except:
                            plot_log.error('Temp 7 days not ploted')                                
                            #plt.show()
                        plt.cla()  #clears the axes
                        time.sleep(aTimer)
                        if Station.HasCam == True:
                            burstCam(Station)
                        try:

                            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
                            plt.gca().xaxis.set_major_locator(mdates.HourLocator())
                            lines = plt.plot_date(d1,t1,'-',xdate=True, ydate=False)
                            plt.setp(lines,color='r', linewidth=2)
                            plt.xlabel('Celsius')
                            plt.title('24h Temperature')
                            plt.grid(True)
                            plot_log.info('Temp saving daily')
                            f_name = '/var/www/reports/tempnow.png'
                            plt.savefig(f_name)
                            if savetodb(f_name, tnow, db) == False:
                                plot_log.error("Plot not saved to DB : " + f_name)
        ##                    if Station.Has_Burst == True:
        ##                        sent,reason = eosp.burstupload(Station, "/temp.png", f1_name)
        ##                        sent,reason = eosp.burstupload(Station, "/tempnow.png", f_name)
                            #plt.show()
                            plot_log.info('Temp finished')
                        except:
                            plot_log.error('Temps 24 hr not ploted')
                        plt.cla()  #clears the axes
                        time.sleep(aTimer)
                        if Station.HasCam == True:
                            burstCam(Station)
                    if Station.Has_Wind > 0:
                        plot_log.info('Wind Starting..')
                        try:

                            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
                            plt.gca().xaxis.set_major_locator(mdates.DayLocator())
                            lines = plt.plot_date(d,ws,'-',xdate=True, ydate=False)
                            lines = plt.plot_date(d,wh,'o',xdate=True, ydate=False)
                            plt.setp(lines,color='b', linewidth=1)
                            plt.title('Wind Speed (gusts)')
                            plt.xlabel('kph')
                            plt.grid(True)
                            plot_log.info('Wind saving weekly')
                            f1_name = '/var/www/reports/wind.png'
                            plt.savefig(f1_name)
                            if savetodb(f1_name, tnow, db) == False:
                                plot_log.error("Plot not saved to DB : " + f1_name)                    
                            #plt.show()   
                        except:
                            plot_log.error('Wind 7 day period not ploted') 
                        plt.cla()  #clears the axes
                        time.sleep(aTimer)
                        if Station.HasCam == True:
                            burstCam(Station)
                        try:

                            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
                            plt.gca().xaxis.set_major_locator(mdates.HourLocator())
                            lines = plt.plot_date(d1,ws1,'-',xdate=True, ydate=False)
                            lines = plt.plot_date(d1,wh1,'o',xdate=True, ydate=False)
                            plt.setp(lines,color='b', linewidth=1)
                            plt.title('24h Wind Speed (gusts)')
                            plt.xlabel('kph')
                            plt.grid(True)
                            plot_log.info('Wind saving daily')
                            f_name = '/var/www/reports/windnow.png'
                            plt.savefig(f_name)
                            if savetodb(f_name, tnow, db) == False:
                                plot_log.error("Plot not saved to DB : " + f_name)
        ##                    if Station.Has_Burst == True:
        ##                        sent,reason = eosp.burstupload(Station, "/wind.png", f1_name)
        ##                        sent,reason = eosp.burstupload(Station, "/windnow.png", f_name)
                            #plt.show()
                            plot_log.info('Wind finished')
                        except:
                            plot_log.error('Wind 24 hrs not ploted')
                        plt.cla()  #clears the axes
                        time.sleep(aTimer)

                    if Station.Has_Pressure > 0:
                        plot_log.info('Pressure starting...')
                        try:

                            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
                            plt.gca().xaxis.set_major_locator(mdates.DayLocator())
                            lines = plt.plot_date(d,bar,'-',xdate=True, ydate=False)    
                            plt.setp(lines,color='g', linewidth=3)
                            plt.title('Pressure')
                            plt.xlabel('kPa')
                            plt.grid(True)
                            plot_log.info('Pressure saving weekly')
                            f1_name = '/var/www/reports/pressure.png'
                            plt.savefig(f1_name)
                            if savetodb(f1_name, tnow, db) == False:
                                plot_log.error("Plot not saved to DB : " + f1_name)
                            
                            #plt.show()
                        except:
                            plot_log.error('Pressure 7 day period not ploted')
                        plt.cla()  #clears the axes
                        time.sleep(aTimer)
                        if Station.HasCam == True:
                            burstCam(Station)
                        try:

                            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
                            plt.gca().xaxis.set_major_locator(mdates.HourLocator())
                            lines = plt.plot_date(d1,bar1,'-',xdate=True, ydate=False)    
                            plt.setp(lines,color='g', linewidth=3)
                            plt.title('24h Pressure')
                            plt.xlabel('kPa')
                            plt.grid(True)
                            plot_log.info('Pressure saving daily')
                            f_name = '/var/www/reports/pressurenow.png'
                            plt.savefig(f_name)
                            if savetodb(f_name, tnow, db) == False:
                                plot_log.error("Plot not saved to DB : " + f_name)
        ##                    if Station.Has_Burst == True:
        ##                        sent,reason = eosp.burstupload(Station, "/pressure.png", f1_name)
        ##                        sent,reason = eosp.burstupload(Station, "/pressurenow.png", f_name)
        ##                    #plt.show()
                            plot_log.info('Pressure finished')
                        except:
                            plot_log.error('Pressure 24 hrs not ploted')
                        plt.cla()  #clears the axes
                except:
                    plot_log.error('Core Data not collected')
                    time.sleep(aTimer)
                if Station.HasCam == True:
                    burstCam(Station)
            if Station.Has_Solar > 0:
                plot_log.info('Solar Starting...')
                try:

                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
                    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
                    lines = plt.plot_date(d,smax,'-',xdate=True, ydate=False)
                    plt.setp(lines,color='r', linewidth=1)
                    lines = plt.plot_date(d,rad,'-',xdate=True, ydate=False)
                    lines = plt.fill_between(d,0,rad)
                    plt.setp(lines,color='y', linewidth=1)
                    plt.title('Solar Radiation')
                    plt.xlabel('W/m2')
                    plt.grid(True)
                    plot_log.info('Solar saving weekly')
                    f1_name = '/var/www/reports/solar.png'
                    plt.savefig(f1_name)
                    if savetodb(f1_name, tnow, db) == False:
                        plot_log.error("Plot not saved to DB : " + f1_name)
                    #plt.show()
                except:
                    plot_log.error('Solar 7 day period not ploted')
                plt.cla()
                time.sleep(aTimer)
                if Station.HasCam == True:
                    burstCam(Station)
                try:

                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
                    plt.gca().xaxis.set_major_locator(mdates.HourLocator())
                    line = plt.plot_date(d1,smax1,'-',xdate=True, ydate=False)
                    plt.setp(lines,color='r', linewidth=1)
                    lines = plt.plot_date(d1,rad1,'-',xdate=True, ydate=False)
                    lines = plt.fill_between(d1,0,rad1)
                    plt.setp(lines,color='y', linewidth=1)
                    plt.title('24h Solar Radiation')
                    plt.xlabel('W/m2')
                    plt.grid(True)
                    plot_log.info('Solar saving daily')
                    f_name = '/var/www/reports/solarnow.png'
                    plt.savefig(f_name)
                    if savetodb(f_name, tnow, db) == False:
                        plot_log.error("Plot not saved to DB : " + f_name)
    ##                if Station.Has_Burst == True:
    ##                    sent,reason = eosp.burstupload(Station, "/solar.png", f1_name)
    ##                    sent,reason = eosp.burstupload(Station, "/solarnow.png", f_name)                      
                    plot_log.info('Solar finished')
                except:
                    plot_log.error('Solar 24 hrs not ploted')
                plt.cla()
                time.sleep(aTimer)
                if Station.HasCam == True:
                    burstCam(Station)

                #plt.show() 


            if Station.Has_Rain > 0:
                plot_log.info('Rain Starting...')
                try:
                    query = "Select WE_DATE, RAIN from CORE_DATE where WE_DATE > '" + dnow.isoformat() + "'"
                    cur.execute(query)
                    result = cur.fetchall()
                    rd = []
                    rain = []
                    for record in result:
                        rd.append(record["WE_DATE"])
                        if float(record["RAIN"]) == 0:
                            rain.append(.01)
                        else:
                            rain.append(float(record["RAIN"]))
                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
                    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
                    #lines = plt.plot_date(rd,rain,'-',xdate=True, ydate=False)    
                    #plt.setp(lines,color='b', linewidth=20)
                    plt.bar(rd,rain)
                    plt.title('Rain')
                    plt.xlabel('mm')
                    plt.grid(True)
                    plot_log.info('Rain saving')
                    f_name = '/var/www/reports/rain.png'
                    plt.savefig(f_name)
                    if savetodb(f_name, tnow, db) == False:
                        plot_log.error("Plot not saved to DB : " + f_name)
    ##                if Station.Has_Burst == True:
    ##                    sent,reason = eosp.burstupload(Station, "/rain.png", f_name)
                    #plt.show()
                    plot_log.info('Rain finished')
                except:
                    plot_log.error('Rain not ploted')
                plt.cla()  #clears the axes
                time.sleep(aTimer)
                if Station.HasCam == True:
                    burstCam(Station)


            if Station.Has_Board > 0 and Station.Has_Temp > 0:
                try:
                    plot_log.info('Board Starting...')
                    query = "Select * from CORE_EXT where WE_DATE_TIME > '" + dnow.isoformat() + "'"
                    cur.execute(query)
                    result = cur.fetchall()
                    for record in result:
                        a = datetime.combine(record["WE_Date"] , (datetime.min + record["WE_Time"]).time())
                        d3.append(a)
                        if record["TEMP_BOARD"] == '---':
                            bt.append(0)
                        else:
                            bt.append(float(record["TEMP_BOARD"]))
                        if record["VOLTS_S"] == '---':
                            vb.append(0)
                        else:
                            vb.append(float(record["VOLTS_S"]))
                        if record["VOLTS_B"] == '---':
                            vs.append(0)
                        else:
                            vs.append(float(record["VOLTS_B"]))
                    ##Get difference between board and outside temps
                    ct = [a - b for a, b in zip(bt, t)]


                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
                    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
                    ##plt.gca().xaxis.set_xaxis_bgcolor = 'red'
                    lines = plt.plot_date(d3,vb,'-',xdate=True, ydate=False)
                    plt.setp(lines,color='r', linewidth=1)
                    lines = plt.plot_date(d3,vs,'-',xdate=True, ydate=False)
                    plt.setp(lines,color='b', linewidth=1)
                    plt.xlabel('Volts')
                    plt.title('Board Voltage')
                    plt.grid(True)
                    plot_log.info('Board saving voltage')
                    f1_name = "/var/www/reports/bvolts.png"
                    plt.savefig(f1_name)
                    if savetodb(f1_name, tnow, db) == False:
                        plot_log.error("Plot not saved to DB : " + f1_name)
                    ##plt.show()
                    plt.cla()  #clears the axes
                except:
                    plot_log.error('Board volts not ploted')
                try:
                    time.sleep(aTimer)
                    if Station.HasCam == True:
                        burstCam(Station)

                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
                    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
                    lines = plt.plot_date(d3,bt,'-',xdate=True, ydate=False)
                    plt.setp(lines,color='r', linewidth=2)
                    lines = plt.plot_date(d3,ct,'-',xdate=True, ydate=False)
                    plt.setp(lines,color='y', linewidth=2)
                    plt.xlabel('Celsius')
                    plt.title('Board Temperature')
                    plt.grid(True)
                    plot_log.info('Board saving temps')
                    f_name ='/var/www/reports/btemp.png'
                    plt.savefig(f_name)
                    if savetodb(f_name, tnow, db) == False:
                        plot_log.error("Plot not saved to DB : " + f_name)
    ##                if Station.Has_Burst == True:
    ##                    sent,reason = eosp.burstupload(Station, "/bvolts.png", f1_name)
    ##                    sent,reason = eosp.burstupload(Station, "/btemp.png", f_name)
                    #plt.show()
                    plot_log.info('Board finished')
                except:
                    plot_log.error('Board temps not ploted')
                plt.cla()  #clears the axes
                time.sleep(aTimer)
                if Station.HasCam == True:
                    burstCam(Station)



                
            if Station.Has_Soil > 0:
                plot_log.info('Soild Starting...')
                try:

                    query = "Select SOIL_ID from SOIL_DATA group by SOIL_ID"
                    cur.execute(query)
                    soils = cur.fetchall()
                    for soil in soils:
                        sid = soil["SOIL_ID"]
                        plot_log.info('Soild ID :' + str(sid))
                        query = "Select * from SOIL_DATA where SOIL_ID = " + str(sid) + " and WE_DATE_TIME > '" + dnow.isoformat() + "'"
                        cur.execute(query)
                        result = cur.fetchall()    
                        for record in result:
                            a = datetime.combine(record["WE_Date"] , (datetime.min + record["WE_Time"]).time())
                            sd.append(a)
                            if record["TEMP"] == '---':
                                st.append(0)
                            else:
                                st.append(float(record["TEMP"]))
                            if record["MOISTURE"] == '---':
                                sm.append(0)
                            else:
                                sm.append(float(record["MOISTURE"]))

            ##        query = "Select * from CORE_SOIL where WE_DATE_TIME > '" + dnow.isoformat() + "'"
            ##        cur.execute(query)
            ##        result = cur.fetchall()    
            ##        for record in result:
            ##            a = datetime.combine(record["WE_Date"] , (datetime.min + record["WE_Time"]).time())
            ##            sd1.append(a)
            ##            st1.append(float(record["TEMP"]))
            ##            sm1.append(float(record["MOISTURE"]))
                        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
                        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
                        lines = plt.plot_date(sd,sm,'-',xdate=True, ydate=False)    
                        plt.setp(lines,color='g', linewidth=3)
                        plt.title('Soil Moisture #' + str(sid))
                        plt.xlabel('%')
                        plt.grid(True)
                        f_name = '/var/www/reports/soilmoisture' + str(sid) + '.png'
                        plt.savefig(f_name)
                        if savetodb(f_name, tnow, db) == False:
                            plot_log.error("Plot not saved to DB : " + f_name)
                        #plt.show()
                except:
                    plot_log.error('Soil not ploted')
                plt.cla()  #clears the axes
                time.sleep(aTimer)
                if Station.HasCam == True:
                    burstCam(Station)
                try:

                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
                    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
                    lines = plt.plot_date(sd,st,'-',xdate=True, ydate=False)    
                    plt.setp(lines,color='g', linewidth=3)
                    plt.title('Soil Temp #' + str(sid))
                    plt.xlabel('Celcius')
                    plt.grid(True)
                    plot_log.info('Soil saving')
                    f_name = '/var/www/reports/soiltemp' + str(sid) + '.png'
                    plt.savefig(f_name)
                    if savetodb(f_name, tnow, db) == False:
                        plot_log.error("Plot not saved to DB : " + f_name)

                    plot_log.info('Soil finished')
                    #plt.show()
                except:
                    plot_log.error('Soil not ploted')
                plt.cla()  #clears the axes
                time.sleep(aTimer)
                if Station.HasCam == True:
                    burstCam(Station)

            ##        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
            ##        plt.gca().xaxis.set_major_locator(mdates.HourLocator())
            ##        lines = plt.plot_date(sd1,sm1,'-',xdate=True, ydate=False)    
            ##        plt.setp(lines,color='g', linewidth=3)
            ##        plt.title('24h Moisture')
            ##        plt.xlabel('%')
            ##        plt.grid(True)
            ##        plt.savefig('/var/www/reports/soilmoisturenow.png')
            ##        #plt.show()
            ##        plt.cla()  #clears the axes
            plot_log.info('FINISHED CYCLE')
            if Station.Has_Burst == True:
                responce, message = eosp.burstupload(Station, "/plotlog.txt", LOG_FILENAME)
                if responce == True:
                    plot_log.info("Log file uploaded")
                else:
                    plot_log.error("Log file upload failed : " + message)
            time.sleep(aTimer)
            if Station.HasCam == True:
                burstCam(Station)


    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print "Exiting Thread..."
        plot_log.info("Exiting via interupt")
        
        

if __name__ == "__main__":

    main()
    


