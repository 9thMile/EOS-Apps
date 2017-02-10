#-*- coding: utf-8 -*-

from array import *
from string import Template
from calendar import monthrange
import sys
import shutil
import os
import re
import string
from datetime import date, datetime, time, timedelta
import MySQLdb as mdb
import httplib, urllib
import eospush as eosp
import eosutils as eosu
import eossql as eoss

has_db = False
has_serial = False
Buff = ""
Buff2 = ""
E1 = ""
NOAAMO = ""
cur = None
db = None

class Station:
    App_Token = ""
    User_Key = ""
    Name = "EOS Default Station"
    Latitude = ""     # D.ddd
    Longitude = ""
    Altitude = ""     #Not set by GPS
    City = ""
    State = ""
    HeatBase = 18
    CoolBase = 18
    ReportBase = '/home/weather'
    BurstOn = False
    Remote_ID = ""
    Remote_Conn = ""
    Burst_USN = ""
    Burst_PWD = ""

def CON_LAT(L):
    NS = " "
    if L > 0:
        NS = "N"
    else:
        NS = "S"
    L = abs(L)
    Deg = int(L)
    Min = (L - int(L))*60
    Sec = (Min - int(Min))*60
    Min = int(Min)
    Sec = int(Sec)

    return str(Deg) + " " + str(Min) + " " + str(Sec) + " " + NS

def CON_LONG(L):
    NS = " "
    if L < 0:
        NS = "W"
    else:
        NS = "E"
    L = abs(L)   
    Deg = int(L)
    Min = (L - int(L))*60
    Sec = (Min - int(Min))*60
    Min = int(Min)
    Sec = int(Sec)

    return str(Deg) + " " + str(Min) + " " + str(Sec) + " " + NS

def DaysinMonth(year,month):
    a = monthrange(year, month)
    return a[1]

class DeltaTemplate(Template):
    delimiter = "%"

def strfdelta(tdelta,fmt):
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    d["M"], d["S"] = divmod(rem, 60)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)



def main():

    global Station
    global has_db
    global cur
    global db
    global NOAAMO

    try:
        db = mdb.connect(host= eoss.SQL.server, port = eoss.SQL.port, user= eoss.SQL.user,passwd= eoss.SQL.password, db= eoss.SQL.database)
        ## Set up a cursor to hold data and execute statments
        cur = db.cursor(mdb.cursors.DictCursor)
        #0 = String, 1 = Int, 2 = Float, 3 = Datetime
        Station.App_Token = eosu.getsetting(db, "APP_TOKEN", 0)
        Station.User_Key = eosu.getsetting(db, "USER_KEY", 0)

        Station.Altitude = str(eosu.getsetting(db, "ALTITUDE", 1)) + " m"
        Station.City = eosu.getsetting(db, "CITY", 0)
        Station.State = eosu.getsetting(db, "STATE", 0)
        Station.Name = eosu.getsetting(db, "NAME", 0)
        Station.Remote_ID = eosu.getsetting(db, "REM_ID", 0)
        if len(Station.Remote_ID) > 1:
            if eosu.getsetting(db,"REM_BURST",1) == 1:
                Station.BurstOn = True
            Station.Remote_Conn  = eosu.getsetting(db, "REM_CONN", 0)
            Station.Burst_USN  = eosu.getsetting(db, "BURST_USN", 0)
            Station.Burst_PWD  = eosu.getsetting(db, "BURST_PWD", 0)
        Station.Latitude = CON_LAT(float(eosu.getsetting(db, "LATITUDE", 0)))
        Station.Longitude = CON_LONG(float(eosu.getsetting(db, "LONGITUDE", 0)))
        Station.HeatBase = eosu.getsetting(db, "HEAT_BASE", 2)
        Station.CoolBase = eosu.getsetting(db, "COOL_BASE", 2)
        rep = eosu.getsetting(db,"REPORT_BASE", 0)
        if rep <> '':
            Station.ReportBase = rep
        
        has_db = True
        os.system('clear')
        sys.stdout.write("Starting Report\n")

    except:
        print "No database connection"
        if len(Station.User_Key) > 0:
            eosp.sendpushover(Station.App_Token, Station.User_Key, "Report Server NOT running - no DB", -1)
        has_db = False
        sys.stdout.write("Not Starting\n")
##    try:
        ##move to report base
    os.chdir(Station.ReportBase)
    
        
    for a in range(0,2):
        
        if a == 0:
            dnow = datetime.now()
            # get first day of this month
            dfirst = datetime(dnow.year,dnow.month,1)
            #last day of previous month back up one day
            d = dfirst - timedelta(days=1)
            NOAA = open("noaaprmo.txt",'w')
             
        else:
            d = datetime.now()
            NOAA = open("noaamo.txt",'w')
            
        days = DaysinMonth(d.year, d.month)
        #dd = d.strftime("%d-%m-%y")
        #get first day of month being done
        d1 = date(d.year, d.month,1)
        print d.strftime('%b. %Y')
        NOAA.write('{:^80}'.format('MONTHLY CLIMATOLOGICAL SUMMARY for ' + d.strftime('%b. %Y')) + '\n')
        NOAA.write('\n')
        NOAA.write('NAME:' + '{:<8}'.format(Station.Name) + ' CITY: ' + '{:<9}'.format(Station.City) + ' STATE: ' + '{:<12}'.format(Station.State) + '\n')
        NOAA.write('ELEV:' + '{:<8}'.format(Station.Altitude) + ' LAT: ' + '{:<14}'.format(Station.Latitude) + ' LONG: ' + '{:<14}'.format(Station.Longitude) + ' \n')
        NOAA.write("\n")
        NOAA.write('{:^80}'.format('TEMPERATURE (C), RAIN  (mm), WIND SPEED (km/hr)') + '\n')
        NOAA.write("\n")
        NOAA.write("                                      HEAT  COOL        AVG\n")
        NOAA.write("    MEAN                              DEG   DEG         WIND                 DOM\n")
        NOAA.write("DAY TEMP  HIGH   TIME   LOW    TIME   DAYS  DAYS  RAIN  SPEED HIGH   TIME    DIR\n")
        NOAA.write("------------------------------------------------------------------------------------\n")
        meantempsum = []
        heatsum = []
        coolsum = []
        rainsum = []
        windspeedsum = []
        windhimax = 0
        windhimaxday = 0
        himaxtemp = -100
        himaxtempday = 1
        lowmintemp = 100
        lowmintempday = 1
        maxrain = 0
        maxrainday = 1
        max32 = 0
        max0 = 0
        min0 = 0
        min18 = 0
        rain02 = 0
        rain2 = 0
        rain20 = 0
        start_date_time = d1.isoformat()


        for b in range(1,days + 1):
            date_time = d1.isoformat()
            a = "Select * from CORE_DATE where WE_DATE = '" + date_time + "'"
            ##print a
            cur.execute(a)
            row = cur.fetchone()
            if row is not None:
                Ndate = '{:>2}'.format(b)
                Nmeantemp = '{:>6}'.format(row["TEMP_AVG"])
                maxtemp = float(row["TEMP_HI"])
                Nmaxtemp = '{:>6}'.format(row["TEMP_HI"])
                lowtemp = float(row["TEMP_LOW"])
                Nlowtemp =  '{:>6}'.format(row["TEMP_LOW"])
                Nheatdd =  '{:>6}'.format(row["HEAT_DD"])
                Ncooldd =  '{:>6}'.format(row["COOL_DD"])
                Nrain = '{:>6}'.format(row["RAIN"])
                Nwindspeed =  '{:>6}'.format(row["WIND_AVG"])
                Nhighwind =  '{:>6}'.format(row["WIND_HI"])
                highwind = float(row["WIND_HI"])
                if row["RAIN"] <> "---":
                    rain = float(row["RAIN"])
                else:
                    rain = 0
                Nrose = '{:>6}'.format(row["WIND_DIR"])
                temptime = " "

                meantempsum.append(float(row["TEMP_AVG"]))
                heatsum.append(float(row["HEAT_DD"]))
                coolsum.append(float(row["COOL_DD"]))
                rainsum.append(rain)
                windspeedsum.append(float(row["WIND_AVG"]))
                if highwind >= windhimax:
                    windhimax = highwind
                    windhimaxday = b
                if maxtemp >= 32:
                    max32 += 1
                if maxtemp <= 0:
                    max0 += 1
                if lowtemp <=0:
                    min0 += 1
                if lowtemp <= -18:
                    min18 += 1
                
                if maxtemp > himaxtemp:
                    himaxtemp = maxtemp
                    himaxtempday = b
                if lowtemp < lowmintemp:
                    lowmintemp = lowtemp
                    lowmintempday = b
                if rain >20:
                    rain20 += 1
                if rain > 2:
                    rain2 += 1
                if rain > .2:
                    rain02 += 1
                if rain > maxrain:
                    maxrain = rain
                    maxrainday = b
                
                    
                
                    

                #a = "Select max(WE_TIME) AS MAX_TIME from CORE_DATA where WE_DATE = '" + date_time + "' and TEMP_OUT = " + str(maxtemp) + " group by WE_DATE"
                a = "Select * from CORE_TIME where WE_Date = '" + date_time + "'"
                cur.execute(a)
                row = cur.fetchone()
                if row is not None:
                    temptime = str(row["MAX_TEMP"])
                    NmaxtempTime = '{:>8}'.format(temptime[:-3])
                    temptime =  str(row["MIN_TEMP"])
                    NlowtempTime ='{:>8}'.format(temptime[:-3])
                    temptime = str(row["MAX_WIND"])
                    NhighwindTime =  '{:>8}'.format(temptime[:-3])

                    
                else:
                    NmaxtempTime = '{:>8}'.format('N/A')
                    NlowtempTime = '{:>8}'.format('N/A')
                    NhighwindTime  = '{:>8}'.format('N/A')
 
            else:
                Ndate = '{:>2}'.format(b)
                Nmeantemp = '{:>6}'.format("")
                Nmaxtemp = '{:>6}'.format("")
                Nlowtemp =  '{:>6}'.format("")
                Nheatdd =  '{:>6}'.format("")
                Ncooldd =  '{:>6}'.format("")
                Nrain = '{:>6}'.format("")
                Nwindspeed =  '{:>6}'.format("")
                Nhighwind =  '{:>6}'.format("")
                NmaxtempTime =   '{:>8}'.format("")
                NlowtempTime  =   '{:>8}'.format("")
                NhighwindTime  =   '{:>8}'.format("")
                Nrose = '{:>6}'.format("")
            db.commit
 

            
            N = Ndate + Nmeantemp + Nmaxtemp + NmaxtempTime + Nlowtemp + NlowtempTime + Nheatdd + Ncooldd + Nrain + Nwindspeed + Nhighwind + NhighwindTime + Nrose + "\n"
            ##print N
            NOAA.write(N)
            d1 = d1 + timedelta(days=1)

        Ndate = '{:>2}'.format("")
        if len(meantempsum) > 0:
            Nmeantemp = '{:>6}'.format(round(sum(meantempsum) / len(meantempsum),1))
        else:
            Nmeantemp = '---'
        Nmaxtemp = '{:>6}'.format(himaxtemp)
        Nlowtemp =  '{:>6}'.format(lowmintemp)
        Nheatdd =  '{:>6}'.format(round(sum(heatsum),0))
        Ncooldd =  '{:>6}'.format(round(sum(coolsum),0))
        Nrain = '{:>6}'.format(sum(rainsum))
        if len(windspeedsum) > 0:
            Nwindspeed =  '{:>6}'.format(round(sum(windspeedsum) / len(windspeedsum),1))
        else:
            Nwindspeed = '---'
        Nhighwind =  '{:>6}'.format(windhimax)
        NmaxtempTime =   '{:^8}'.format(himaxtempday)
        NlowtempTime  =   '{:^8}'.format(lowmintempday)
        NhighwindTime  =   '{:^8}'.format(windhimaxday)

        a = "Select count(WIND_DIR), WIND_DIR from CORE_DATE where WE_DATE >= '" + start_date_time + "' AND WE_DATE <= '" + date_time + "' AND WIND_DIR <> '---' group by WIND_DIR order by count(WIND_DIR) desc limit 0,1"
        cur.execute(a)
        row = cur.fetchone()
        db.commit()
        if row is not None:
            Nrose = '{:>6}'.format(row["WIND_DIR"])

        else:
            Nrose = '{:>6}'.format("---")
        
        NOAA.write("------------------------------------------------------------------------------------\n")
        
        N = Ndate + Nmeantemp + Nmaxtemp + NmaxtempTime + Nlowtemp + NlowtempTime + Nheatdd + Ncooldd + Nrain + Nwindspeed + Nhighwind + NhighwindTime + Nrose + "\n"
        ##print "Done" + str(b)
        NOAA.write(N)           
        NOAA.write("\n")

        NOAA.write('Max >=  32.0:{:>3}\n'.format(max32))
        NOAA.write('Max >=   0.0:{:>3}\n'.format(max0))
        NOAA.write('Min <=   0.0:{:>3}\n'.format(min0))
        NOAA.write('Min <= -18.0:{:>3}\n'.format(min18))

        NOAA.write('Max rain: {:>3} on '.format(maxrain) + '{:>2}\n'.format(maxrainday))
        NOAA.write('Days of Rain:' + '{:>3} (> .2 mm) '.format(rain02) + '{:>3} (> 2 mm) '.format(rain2) + '{:>3} (> 20 mm)\n'.format(rain20))

        NOAA.write('Heat Base:{:>6} '.format(Station.HeatBase) + 'Cool Base:{:>6} Method: Integration\n'.format(Station.CoolBase))
        NOAA.close()
        if len(Station.Burst_USN) > 0:
            sent,reason = eosp.burstupload(Station, "/" + NOAA.name, NOAA.name)

        
        shutil.copy(NOAA.name, start_date_time[:7] + "mo.txt")
        if len(Station.Burst_USN) > 0:
            sent,reason = eosp.burstupload(Station, "/" + start_date_time[:7] + "mo.txt" , start_date_time[:7] + "mo.txt")


    
    
    
##    if len(Station.User_Key) > 0:
##            eosp.sendpushover(Station.App_Token, Station.User_Key, "NOAA Monthy Reports Completed", -1)
    quit
        

##    except Exception,e:
##        print "File error"
##        print str(e)
##        if len(Station.User_Key) > 0:
##                Send_PushOver(Station.App_Token, Station.User_Key, "NOAA Reports failed",-1)

if __name__ ==  '__main__':

    main()

