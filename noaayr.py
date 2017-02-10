#-*- coding: utf-8 -*-

from array import *
from string import Template
from calendar import monthrange
from decimal import Decimal
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

    global SQL
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
    a = 1
    if a == a:
        ##Remove previous report
        os.chdir(Station.ReportBase)
        #Get yearly normals
        a = "Select DESCRIPT from STATION where ID = 49"
        cur.execute(a)
        row = cur.fetchone()
        if row is not None:
            t = row["DESCRIPT"]
            tempnorm = t.split(',')
        db.commit
        a = "select DESCRIPT from STATION where ID = 50"
        cur.execute(a)
        row = cur.fetchone()
        if row is not None:
            t = row["DESCRIPT"]
            rainnorm = t.split(',')
        db.commit
        monthname = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        for a in range(0,2):
            
            if a == 0:
                dnow = datetime.now()
                #get previous year
                d = dnow - timedelta(days=365)
                NOAA = open("noaapryr.txt",'w')
            else:
                d = datetime.now()
                NOAA = open("noaayr.txt",'w')
            
            #dd = d.strftime("%d-%m-%y")
            #get first date of year
            d1 = date(d.year, 1,1)
            print d1.strftime('%b. %Y')
            NOAA.write('{:^80}'.format('ANNUAL CLIMATOLOGICAL SUMMARY') + '\n')
            NOAA.write('\n')
            NOAA.write('NAME:' + '{:<8}'.format(Station.Name) + ' CITY: ' + '{:<9}'.format(Station.City) + ' STATE: ' + '{:<12}'.format(Station.State) + '\n')                                                                                                                
            NOAA.write('ELEV:' + '{:<8}'.format(Station.Altitude) + ' LAT: ' + '{:<14}'.format(Station.Latitude) + ' LONG: ' + '{:<14}'.format(Station.Longitude) + ' \n')
            NOAA.write("\n")
            NOAA.write('{:^80}'.format('TEMPERATURE (C), HEAT BASE = ' + '{:>4}'.format(Station.HeatBase) + ', COOL BASE = ' + '{:>4}'.format(Station.CoolBase)) + '\n')
            NOAA.write("\n")
            NOAA.write("                          DEP.  HEAT  COOL\n")
            NOAA.write("        MEAN  MEAN        FROM  DEG   DEG                        MAX  MAX  MIN  MIN\n")
            NOAA.write(" YR MO  MAX   MIN   MEAN  NORM  DAYS  DAYS  HI  DATE  LOW  DATE  >=32 <=0  <=0  <=-18\n")
            NOAA.write("-------------------------------------------------------------------------------------\n")
            meanmaxsum= []
            meanminsum = []
            meanmeansum = []
            meansum = []
            heatsum = []
            coolsum = []
            maxhisum = []
            minlowsum = []
            max32sum = []
            max0sum = []
            min0sum = []
            min18sum =[]
            deptempsum = []
            monthsum = []
            monthhi = 1
            monthlow = 1
            monthhivalue = -100
            monthlowvalue = 100

            for b in range(1,13):
                d1 = date(d.year,b,1)
                startdate_time = d1.isoformat()
                if b == 12:
                    d2 = date(d.year + 1,1,1)
                else:
                    d2 = date(d.year,b + 1,1)
                
                enddate_time = d2.isoformat()
                a = "Select COUNT(TEMP_HI) as C, ROUND(AVG(cast(TEMP_HI as DECIMAL(10,2))),1) as MEANMAX, ROUND(AVG(cast(TEMP_LOW as DECIMAL(10,2))),1) as MEANLOW, ROUND(MAX(cast(TEMP_HI as DECIMAL(10,2))),1) as MAXT, ROUND(MIN(cast(TEMP_LOW as DECIMAL(10,2))),1) as MINT, ROUND(AVG(cast(TEMP_AVG as DECIMAL(10,2))),1) as MEANT," + \
                    "ROUND(SUM(cast(HEAT_DD as DECIMAL(10,2))),0) as HEAT, ROUND(SUM(cast(COOL_DD as DECIMAL(10,2))),0) as COOL, SUM(IF(cast(TEMP_HI as DECIMAL(10,2))>=32,1,0)) as MAX32, " + \
                    "SUM(IF(cast(TEMP_HI as DECIMAL(10,2))<=0,1,0)) as MAX0, SUM(IF(cast(TEMP_LOW as DECIMAL(10,2)) <=0,1,0)) as MIN0, SUM(IF(cast(TEMP_LOW as DECIMAL(10,2)) <=-18,1,0)) as MIN18 " + \
                    "from CORE_DATE where WE_DATE >= '" + startdate_time + "' and WE_DATE < '" + enddate_time + "'"
                #print a
                Nyear = '{:>3}'.format(d1.strftime('%y'))
                Nmonth = '{:>3}'.format(d1.month)
                Nmeantemp = '{:>6}'.format("")
                Nmeanmaxtemp = '{:>6}'.format("")
                Nmeanlowtemp = '{:>6}'.format("")
                Nmaxtemp = '{:>6}'.format("")
                Nlowtemp =  '{:>6}'.format("")
                Nheatdd =  '{:>6}'.format("")
                Ncooldd =  '{:>6}'.format("")
                Nmax32 = '{:>5}'.format("")
                Nmax0 = '{:>5}'.format("")
                Nmin0 = '{:>5}'.format("")
                Nmin18 = '{:>5}'.format("")
                Ndepart = '{:>5}'.format("")
                NlowtempTime = '{:>4}'.format('')
                NmaxtempTime = '{:>4}'.format('')
                cur.execute(a)
                row = cur.fetchone()
                if row is not None:
                    if row["C"] > 0:
                        Nmaxtemp = '{:>6}'.format(row["MAXT"])
                        maxtemp = row["MAXT"]
                        maxhisum.append(maxtemp)
                        if maxtemp > monthhivalue:
                            monthhivalue = maxtemp
                            monthhi = b

                        Nmeanmaxtemp = '{:>6}'.format(row["MEANMAX"])
                        meanmaxsum.append(row["MEANMAX"])
                        Nmeanlowtemp = '{:>6}'.format(row["MEANLOW"])
                        meanminsum.append(row["MEANLOW"])
                        Nmeantemp = '{:>6}'.format(row["MEANT"])
                        meanmeansum.append(row["MEANT"])
                        meantemp = row["MEANT"]
                        lowtemp = row["MINT"]
                        if lowtemp < monthlowvalue:
                            monthlowvalue = lowtemp
                            monthlow = b
                        Nlowtemp =  '{:>6}'.format(row["MINT"])
                        minlowsum.append(row["MINT"])
                        Nheatdd =  '{:>6}'.format(row["HEAT"])
                        heatsum.append(row["HEAT"])
                        Ncooldd =  '{:>6}'.format(row["COOL"])
                        coolsum.append(row["COOL"])
                        Nmax32 = '{:>5}'.format(row["MAX32"])
                        max32sum.append(row["MAX32"])
                        Nmax0 = '{:>5}'.format(row["MAX0"])
                        max0sum.append(row["MAX0"])
                        Nmin0 = '{:>5}'.format(row["MIN0"])
                        min0sum.append(row["MIN0"])
                        Nmin18 = '{:>5}'.format(row["MIN18"])
                        min18sum.append(row["MIN18"])
                        monthnorm = Decimal(tempnorm[b-1])
                        monthsum.append(monthnorm)
                        if monthnorm >= meantemp:
                            deptemp = abs(monthnorm - meantemp) * -1
                            Ndepart = '{:>5}'.format(deptemp)
            
                        else:
                            deptemp = abs(meantemp - monthnorm)
                            Ndepart = '{:>5}'.format(deptemp)

                        deptempsum.append(deptemp)

                        temptime = " "
                        

                        a = "Select WE_DATE AS MAX_DATE from CORE_DATE where WE_DATE >= '" + startdate_time + "' and WE_DATE < '" + enddate_time + "' order by cast(TEMP_HI as DECIMAL(10,2)) desc limit 0,1"

                        cur.execute(a)
                        row = cur.fetchone()
                        if row is not None:
                            tempdate = row["MAX_DATE"]
                            NmaxtempTime = '{:>4}'.format(tempdate.day)
                        else:
                            NmaxtempTime = '{:>4}'.format('N/A')
                        db.commit
                        a = "Select WE_DATE AS MIN_DATE from CORE_DATE where WE_DATE >= '" + startdate_time + "' and WE_DATE < '" + enddate_time + "' order by cast(TEMP_LOW as DECIMAL(10,2)) limit 0,1"
                        #print a
                        cur.execute(a)
                        row = cur.fetchone()
                        if row is not None:
                            tempdate =  row["MIN_DATE"]
                            NlowtempTime ='{:>4}'.format(tempdate.day)
                        else:
                            NlowtempTime = '{:>4}'.format('N/A')

                        db.commit

                db.commit
     

                
                N = Nyear + Nmonth + Nmeanmaxtemp + Nmeanlowtemp + Nmeantemp + Ndepart + Nheatdd + Ncooldd + Nmaxtemp + NmaxtempTime + Nlowtemp + NlowtempTime + Nmax32 + Nmax0 + Nmin0 + Nmin18 + "\n"


                NOAA.write(N)
                
            NOAA.write("-------------------------------------------------------------------------------------\n")
            if len(meanmaxsum) > 0:
                Nmeanmaxtemp = '{:>6}'.format(round(sum(meanmaxsum) / len(meanmaxsum),1))
            else:
                Nmeanmaxtemp = '---'
            if len(meanminsum) > 0:
                Nmeanlowtemp = '{:>6}'.format(round(sum(meanminsum) / len(meanminsum),1))
            else:
                Nmeanlowtemp = '---'
            if len(meanmeansum) > 0:
                Nmeantemp = '{:>6}'.format(round(sum(meanmeansum) / len(meanmeansum),1))
            else:
                Nmeantemp = '---'
            if len(monthsum) > 0:
                monthnorm = Decimal(round(sum(monthsum)/len(monthsum),1))
            else:
                monthnorm = '---'
            if len(deptempsum) > 0:
                Ndepart = '{:>5}'.format(round(sum(deptempsum) / len(deptempsum),1))
            else:
                Ndepart = '---'
            Nheatdd = '{:>6}'.format(sum(heatsum))
            Ncooldd = '{:>6}'.format(sum(coolsum))           
            Nmaxtemp = '{:>6}'.format(round(monthhivalue,1))
            NmaxtempTime = '{:>4}'.format(monthname[monthhi-1])            
            Nlowtemp = '{:>6}'.format(round(monthlowvalue,1))
            NlowtempTime = '{:>4}'.format(monthname[monthlow-1])
            Nmax32 = '{:>5}'.format(sum(max32sum))
            Nmax0 = '{:>5}'.format(sum(max0sum))
            Nmin0 = '{:>5}'.format(sum(min0sum))
            Nmin18 = '{:>5}'.format(sum(min18sum))

            

            N = '      ' + Nmeanmaxtemp + Nmeanlowtemp + Nmeantemp + Ndepart + Nheatdd + Ncooldd + Nmaxtemp + NmaxtempTime + Nlowtemp + NlowtempTime + Nmax32 + Nmax0 + Nmin0 + Nmin18 + "\n"
            NOAA.write(N)    
            NOAA.write('\n')
            
            ##Need to do Rain data
            if eosu.getsetting(db,"RAIN_COUNT", 1) >0:
                NOAA.write('{:^80}'.format('PRECIPITATION (mm)') + '\n')
                NOAA.write('\n')
                NOAA.write("               DEP.   MAX        DAYS OF RAIN\n")
                NOAA.write("               FROM   OBS.          OVER\n")
                NOAA.write(" YR MO  TOTAL  NORMAL DAY  DATE  .2   2   20\n")
                NOAA.write("---------------------------------------------\n")
                rainsum = []
                deptrainsum = []
                monthhi = 1
                monthhivalue = 0
                over02sum = []
                over2sum = []
                over20sum = []
                
                for b in range(1,13):
                    d1 = date(d.year,b,1)
                    startdate_time = d1.isoformat()
                    if b == 12:
                        d2 = date(d.year + 1,1,1)
                    else:
                        d2 = date(d.year,b + 1,1)
                    
                    enddate_time = d2.isoformat()
                    a = "Select COUNT(RAIN) as C, ROUND(MAX(cast(RAIN as DECIMAL(10,2))),1) as MAXRAIN, ROUND(SUM(cast(RAIN as DECIMAL(10,2))),1) as SUMRAIN, SUM(IF(cast(RAIN as DECIMAL(10,2)) >.2,1,0)) as OVER02, SUM(IF(cast(RAIN as DECIMAL(10,2)) >2,1,0)) as OVER2, SUM(IF(cast(RAIN as DECIMAL(10,2)) >20,1,0)) as OVER20 from CORE_DATE where WE_DATE >= '" + startdate_time + "' and WE_DATE < '" + enddate_time + "'"
                    #print a
                    Nyear = '{:>3}'.format(d1.strftime('%y'))
                    Nmonth = '{:>3}'.format(d1.month)
                    Nsumrain = '{:>6}'.format("")
                    Ndepart = '{:>7}'.format("")
                    Nmaxrain = '{:>6}'.format("")
                    Nmaxdate ='{:>6}'.format("")
                    Nover02 ='{:>5}'.format("")
                    Nover2 ='{:>5}'.format("")
                    Nover20 ='{:>5}'.format("")
                    cur.execute(a)
                    row = cur.fetchone()
                    if row is not None:
                        if row["C"] > 0:        
                            Nsumrain = '{:>6}'.format(row["SUMRAIN"])
                            sumrain = row["SUMRAIN"]

                            rainsum.append(sumrain)
                            monthnorm = Decimal(rainnorm[b-1])
                            if monthnorm >= sumrain:
                                deptrain =  abs(monthnorm - sumrain) * -1
                                Ndepart = '{:>7}'.format(deptrain)
                            else:
                                deptrain = abs(sumrain - monthnorm)
                                Ndepart = '{:>7}'.format(deptrain)                            

                            deptrainsum.append(deptrain)
                            Nmaxrain = '{:>6}'.format(row["MAXRAIN"])
                            maxrain = row["MAXRAIN"]
                            if maxrain > monthhivalue:
                                monthhivalue = maxrain
                                monthhi = b
                            Nmaxdate ='{:>6}'.format("")
                            Nover02 ='{:>5}'.format(row["OVER02"])
                            over02sum.append(row["OVER02"])
                            Nover2 ='{:>5}'.format(row["OVER2"])
                            over2sum.append(row["OVER2"])
                            Nover20 ='{:>5}'.format(row["OVER20"])
                            over20sum.append(row["OVER20"])
                            a = "Select WE_DATE AS MAX_DATE from CORE_DATE where WE_DATE >= '" + startdate_time + "' and WE_DATE < '" + enddate_time + "' order by cast(RAIN as DECIMAL(10,2)) desc limit 0,1"    
                            cur.execute(a)
                            row = cur.fetchone()
                            if row is not None:
                                tempdate = row["MAX_DATE"]
                                Nmaxdate = '{:>4}'.format(tempdate.day)
                            else:
                                Nmaxdate = '{:>4}'.format('N/A')
                            db.commit

                    N = Nyear + Nmonth + Nsumrain + Ndepart + Nmaxrain + Nmaxdate + Nover02 + Nover2 + Nover20 + "\n"
                    NOAA.write(N)


                NOAA.write("---------------------------------------------\n")
                Nyear = '{:>3}'.format('')
                Nmonth = '{:>3}'.format('')
                Nsumrain = '{:>6}'.format(sum(rainsum))
                Ndepart = '{:>7}'.format(sum(deptrainsum))
                Nmaxrain = '{:>6}'.format(monthhivalue)
                Nmaxdate ='{:>4}'.format(monthname[monthhi-1])
                Nover02 ='{:>5}'.format(sum(over02sum))
                Nover2 ='{:>5}'.format(sum(over2sum))
                Nover20 ='{:>5}'.format(sum(over20sum))

                N = Nyear + Nmonth + Nsumrain + Ndepart + Nmaxrain + Nmaxdate + Nover02 + Nover2 + Nover20 + "\n"
                NOAA.write(N)
                
            ##Need to do wind data
            if eosu.getsetting(db, "WIND_COUNT", 1) > 0:
                NOAA.write('\n')
                NOAA.write('{:^80}'.format('WIND SPEED (km/hr)') + '\n')
                NOAA.write('\n')
                NOAA.write("                         DOM\n")
                NOAA.write(" YR MO  AVG.  HI   DATE  DIR\n")
                NOAA.write("-----------------------------------\n")
                windavgsum = []
                monthhi = 1
                monthhivalue = 0
                
                for b in range(1,13):
                    d1 = date(d.year,b,1)
                    startdate_time = d1.isoformat()
                    if b == 12:
                        d2 = date(d.year + 1,1,1)
                    else:
                        d2 = date(d.year,b + 1,1)
                    
                    enddate_time = d2.isoformat()
                    a = "Select COUNT(WIND_HI) as C, ROUND(AVG(cast(WIND_AVG as DECIMAL(10,2))),0) as SPEED, ROUND(MAX(cast(WIND_HI as DECIMAL(10,2))),0) as HIGH from CORE_DATE where WE_DATE >= '" + startdate_time + "' and WE_DATE < '" + enddate_time + "'"

                    Nyear = '{:>3}'.format(d1.strftime('%y'))
                    Nmonth = '{:>3}'.format(d1.month)
                    Nwindavg = '{:>6}'.format("")
                    Nwindhi = '{:>6}'.format("")
                    Nwinddate = '{:>5}'.format("")
                    Nrose = '{:>6}'.format("")
                    cur.execute(a)
                    row = cur.fetchone()
                    if row is not None:
                        if row["C"] > 0:        
                            Nwindavg = '{:>6}'.format(row["SPEED"])
                            windavgsum.append(row["SPEED"])

                            Nwindhi = '{:>6}'.format(row["HIGH"])
                            maxwind = row["HIGH"]
                            if maxwind > monthhivalue:
                                monthhivalue = maxwind
                                monthhi = b
                            a = "Select WE_DATE AS MAX_DATE from CORE_DATE where WE_DATE >= '" + startdate_time + "' and WE_DATE < '" + enddate_time + "' order by cast(WIND_HI as DECIMAL(10,2)) desc limit 0,1"
    
                            cur.execute(a)
                            row = cur.fetchone()
                            if row is not None:
                                tempdate = row["MAX_DATE"]
                                Nwinddate = '{:>4}'.format(tempdate.day)
                            else:
                                Nwinddate = '{:>4}'.format('N/A')
                            db.commit                            

                            
                            a = "Select count(WIND_DIR), WIND_DIR from CORE_DATA where WE_DATE >= '" + startdate_time + "' AND WE_DATE < '" + enddate_time + "' AND WIND_DIR <> '---' group by WIND_DIR order by count(WIND_DIR) desc limit 0,1"
                            cur.execute(a)
                            row = cur.fetchone()
                            db.commit()
                            if row is not None:
                                Nrose = '{:>6}'.format(row["WIND_DIR"])

                            else:
                                Nrose = '{:>6}'.format("---")
                    
                    N = Nyear + Nmonth + Nwindavg + Nwindhi + Nwinddate + Nrose + "\n"

                    NOAA.write(N)
                NOAA.write("-----------------------------------\n")
                Nyear = '{:>3}'.format('')
                Nmonth = '{:>3}'.format('')
                if len(windavgsum) > 0:
                    Nwindavg = '{:>6}'.format(round(sum(windavgsum)/ len(windavgsum),1))
                else:
                    Nwindavg = '---'
                Nwindhi = '{:>6}'.format(monthhivalue)
                Nwinddate = '{:>5}'.format(monthname[monthhi-1])
                d1 = date(d1.year,1,1)
                d2 = date(d1.year +1,1,1)
                startdate_time = d1.isoformat()
                enddate_time = d2.isoformat()
                a = "Select count(WIND_DIR), WIND_DIR from CORE_DATA where WE_DATE >= '" + startdate_time + "' AND WE_DATE < '" + enddate_time + "' AND WIND_DIR <> '---' group by WIND_DIR order by count(WIND_DIR) desc limit 0,1"
                cur.execute(a)
                row = cur.fetchone()
                db.commit()
                if row is not None:
                    Nrose = '{:>6}'.format(row["WIND_DIR"])

                else:
                    Nrose = '{:>6}'.format("---")
                N = Nyear + Nmonth + Nwindavg + Nwindhi + Nwinddate + Nrose + "\n"
                NOAA.write(N)
                NOAA.close()
                if len(Station.Burst_USN) > 0:
                    sent,reason = eosp.burstupload(Station, "/" + NOAA.name, NOAA.name)

                
                shutil.copy(NOAA.name, startdate_time[:4] + "yr.txt")
                if len(Station.Burst_USN) > 0:
                    sent,reason = eosp.burstupload(Station, "/" + startdate_time[:4] + "yr.txt" , startdate_time[:4] + "yr.txt")
                    
            
##        if len(Station.User_Key) > 0:
##            eosp.sendpushover(Station.App_Token, Station.User_Key, "NOAA Monthy Reports Completed", -1)
        quit
        

##    except, Exception e:
##        print "File error" + str(e)
        

if __name__ ==  '__main__':

    main()

