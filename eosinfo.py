#!/usr/bin/env python
import sys
import socket
import fcntl
import struct
import netifaces
import urllib2
import subprocess
from time import sleep
from datetime import date, datetime, time, timedelta, tzinfo
import pifacecad
import eossql as eoss
import eosutils as eosu
import MySQLdb as mdb

UPDATE_INTERVAL = 3  #seconds
STARTUP = 130  #change to 130 for production

##Set station IP's in main sub
SITE = []

temperature_symbol = pifacecad.LCDBitmap(
    [0x4, 0x4, 0x4, 0x4, 0xe, 0xe, 0xe, 0x0])
memory_symbol = pifacecad.LCDBitmap(
    [0xe, 0x1f, 0xe, 0x1f, 0xe, 0x1f, 0xe, 0x0])

trendup_symbol = pifacecad.LCDBitmap(
    [0x4, 0xe, 0x1f, 0x4, 0x4, 0x4, 0x4, 0x4])

trenddown_symbol = pifacecad.LCDBitmap(
    [0x4, 0x4, 0x4, 0x4, 0x4, 0x1f, 0xe, 0x4])


temp_symbol_index, memory_symbol_index, trendup_symbol_index, trenddown_symbol_index = 0, 1, 2, 3

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915, # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
        )[20:24])

def wait_for_user():
    cad.lcd.clear()
    cad.lcd.write("Suspending...")
    sleep(3)
    cad.lcd.clear()
    cad.lcd.write("On -> (1) & (2)")
    sleep(5)
    cad.lcd.clear()
    cad.lcd.display_off()
    cad.lcd.backlight_off()
    while cad.switches[0].value == 0 and cad.switches[1].value == 0:
        sleep(5)
    cad.lcd.backlight_on()
    cad.lcd.display_on()
    cad.lcd.write("...Starting")
    sleep(2)
        
def do_status():
    cad.lcd.clear()
    cad.lcd.write("Checking status...")
    sleep(2)
    db = mdb.connect(host= SITE[0], port = eoss.SQL.port, user= eoss.SQL.user,passwd= eoss.SQL.password, db= eoss.SQL.database)
    cur = db.cursor(mdb.cursors.DictCursor)
    try:
        cur.execute("SELECT COUNT(W_TIME) as C FROM FEED")
        db.commit()
        row = cur.fetchone()
        if row is not None:
            cfeed = row["C"]
        cur.execute("SELECT W_TIME FROM FEED order by W_TIME desc limit 0,1")
        db.commit()
        row = cur.fetchone()
        if row is not None:
            tfeed = row["W_TIME"]
        
        cur.execute("SELECT COUNT(W_TIME) as C FROM FEED where IS_DONE = 1 and W_TIME > DATE_SUB(sysdate(),INTERVAL 1 MINUTE)")
        db.commit()
        row = cur.fetchone()
        if row is not None:
            feed = row["C"]
        cur.execute("SELECT COUNT(WE_DATE_TIME) as C FROM CORE_DATA where WE_DATE_TIME > DATE_SUB(UTC_TIMESTAMP(),INTERVAL 11 MINUTE)")
        db.commit()
        row = cur.fetchone()
        if row is not None:
            afeed = row["C"]
        cur.execute("SELECT WE_DATE_TIME FROM CORE_DATA order by WE_DATE_TIME desc limit 0,1")
        db.commit()
        row = cur.fetchone()
        if row is not None:
            larch = row["WE_DATE_TIME"]
        cur.execute("SELECT INT_VALUE as C FROM STATION where LABEL = 'REM_ID'")
        db.commit()
        row = cur.fetchone()
        if row is not None:
            netup = row["C"]
        cad.lcd.clear()
        cad.lcd.write("Feed Count = " + str(cfeed))
        if feed >0:
            cad.lcd.write("\nEOS Processing")
            sleep(2)
            cad.lcd.clear()
            cad.lcd.write("Feed Time local\n" + tfeed.strftime("%d-%b %I:%M:%S"))
                
        else:
            sleep(2)
            cad.lcd.clear()
            cad.lcd.write("ERROR\nEOS NOT RUNNING!")
        sleep(2)
        cad.lcd.clear()
        if afeed > 0:
            cad.lcd.write("Last Archive UTC\n" + larch.strftime("%d-%b %I:%M"))
        else:
            cad.lcd.write("ERROR\nNOT ARCHIVING")
        sleep(2)
        if netup > 0:
            cad.lcd.clear()
            cad.lcd.write("Uploads working")
            sleep(2)
        cur.execute("SELECT INT_VALUE as I, STR_VALUE as F FROM STATION where LABEL ='HAS_FAN'")
        db.commit()
        row = cur.fetchone()
        if row is not None:
            hasfan = row["I"]
            fanstate = row["F"]
            cad.lcd.clear()
            cad.lcd.write("Fan State:\n " + fanstate)
            sleep(2)
        else:
            cad.lcd.clear()
            cad.lcd.write("Fan not enabled")
            sleep(1)
        cur.execute("SELECT * FROM BOARD order by W_TIME desc limit 0,1")
        db.commit()
        row = cur.fetchone()
        if row is not None:
            B_Volt = row['B_VOLTAGE']
            S_Volt = row['S_VOLTAGE']
            C_Temp = row['C_TEMP']
            cad.lcd.clear()
            cad.lcd.write("Board Temp: " + str(C_Temp))
            m = "\nBvolt :" + str(B_Volt) + " Svolt : " + str(S_Volt)
            cad.lcd.write(m)
            slide(m)
        
        
        
    except:
        cad.lcd.write("\nN/A")

    sleep(2)

def do_startup():
    for x in range(STARTUP, 1, -1):
        cad.lcd.clear()
        cad.lcd.write(str(x))
        sleep(1)
        
def do_versions():
    cad.lcd.clear()
    cad.lcd.write("Checking Versions...")
    sleep(3)
    db = mdb.connect(host= SITE[0], port = eoss.SQL.port, user= eoss.SQL.user,passwd= eoss.SQL.password, db= eoss.SQL.database)
    cur = db.cursor(mdb.cursors.DictCursor)
    try:
        eor_version = eosu.getsetting(db, "EOR_VERSION", 0)
        eos_version = eosu.getsetting(db, "EOS_VERSION", 0)
        cur.execute("SELECT VERSION FROM BOARD order by W_TIME desc limit 0,1")
        db.commit()
        row = cur.fetchone()
        if row is not None:
             version = row["VERSION"]
        else:
            version = "N/A"
            
        cad.lcd.clear()
        cad.lcd.write("Firmware:\n  " + version)
        sleep(3)
        cad.lcd.clear()
        cad.lcd.write("EOR Software:\n  " + eor_version)
        sleep(3)
        cad.lcd.clear()
        cad.lcd.write("EOS Software:\n  " + eos_version)
        sleep(3)
        cad.lcd.clear()
        
    except:
        cad.lcd.clear()
        cad.lcd.write("ERROR:/nNo data available")
        sleep(5)
        cad.lcd.clear()

def do_netifaces():
    cad.lcd.clear()
    cad.lcd.write("Interfaces..")
    sleep(1)
    f = netifaces.interfaces()
    for nf in f:
        try:
            
            addrs = netifaces.ifaddresses(nf)
            inet = []
            if len(addrs) > 0:                
                inet = addrs[netifaces.AF_INET]
                addr = inet[0]['addr']
                link = addrs[netifaces.AF_LINK]
                mac = link[0]['addr']
                cad.lcd.clear()
                cad.lcd.write(nf + " IP\n" + addr)
                sleep(2)
                cad.lcd.clear()
                cad.lcd.write(nf + " MAC \n" + mac)
                sleep(1)
                slide(mac)
                sleep(1)
            else:
                cad.lcd.clear()
                cad.lcd.write(nf + " Not Available")
                sleep(2)
        except Exception,e:
            cad.lcd.clear()
            er = "No Connection : " + str(e)
            cad.lcd.write("ERROR on:" + nf + "\n" + er)
            if len(er) > 15:
                slide(er)
            else:
                sleep(2)
##    try:
##        
##        gws = netifaces.gateways()
##        dgws = gws['default'][netifaces.AF_INET]
##        cad.lcd.clear()
##        cad.lcd.write("Gateway " + dgws[1] + "\n" + dgws[0])
##        sleep(2)
##    except Exception,e:
##        cad.lcd.clear()
##        er = "No Connection : " + str(e)
##        cad.lcd.write("ERROR on Gateway\n" + er)
##        if len(er) > 15:
##            slide(er)
##        else:
##            sleep(2)

    cad.lcd.clear()
    cad.lcd.write("Checking\nInternet")
    sleep(2)
    cad.lcd.clear()
    db = mdb.connect(host= SITE[0], port = eoss.SQL.port, user= eoss.SQL.user,passwd= eoss.SQL.password, db= eoss.SQL.database)
    cur = db.cursor(mdb.cursors.DictCursor)
    try:
        cur.execute("SELECT STR_VALUE as S FROM STATION where LABEL ='REM_CONN'")
        db.commit()
        row = cur.fetchone()
        if row is not None:
            
            website = row["S"]
            if len(website) > 1:
                cad.lcd.write("Checking:\n " + website)
                slide(website)
                cad.lcd.clear()
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                try:
                    s.connect((website, 80))
                    cad.lcd.write("Connection Open")
                    sleep(2)
                except Exception,e:
                    cad.lcd.write("Connection refused\n" + str(e))
                    slide(str(e))
                s.close()
            else:
                cad.lcd.write("Checking:\n " + "google.com")
                sleep(1)
                cad.lcd.clear()
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                try:
                    s.connect(("google.com", 80))
                    cad.lcd.write("Connection Open")
                    sleep(2)
                except Exception,e:
                    cad.lcd.write("Connection refused\n" + str(e))
                    slide(str(e))
                s.close()              
    except:
        cad.lcd.clear()
        

def slide(m):
    cad.lcd.left_to_right()  
    x = len(m) -15
    if x > 0:               
        while x <> 0:
            cad.lcd.move_left()
            x = x -1
            sleep(.5)
            while cad.switches[4].value == 1:
               sleep(1)
            while cad.switch_port.value == 64:
                if x < len(m) - 15:                    
                    cad.lcd.move_right()
                    x = x + 1
                    sleep(.25)
            while cad.switch_port.value == 128:
                if x > 0:
                    print cad.switch_port.value
                    cad.lcd.move_left()
                    sleep(.25)
                    x = x -1
        sleep(1)
    else:
        sleep(3)
def show_sysinfo():
    Station = 0
    cycle = 0
    var = 0
    UP = UPDATE_INTERVAL
    try:
        
        while var == 0:

            if cad.switch_port.value == 64:
                if UP >2:
                    UP = UP -1
                    cad.lcd.clear()
                    cad.lcd.write("Update = " + str(UP))
                    sleep(1)
            elif cad.switch_port.value == 128:
                UP = UP + 1
                cad.lcd.clear()
                cad.lcd.write("Update = " + str(UP))
                sleep(1)            
            
            ##User is Suspending / display_off
            ##print cycle
            if cad.switches[0].value == 1:
                cad.lcd.clear()
                cad.lcd.write("1-Suspend\n2-Quit 3-Cancel")
                sleep(3)
                while cad.switches[0].value + cad.switches[1].value + cad.switches[2].value == 0:
                    sleep(1)
                if cad.switches[0].value == 1:
                    db.close()
                    wait_for_user()
                    cycle = 0
                elif cad.switches[1].value == 1:
                    var = 1 
                    cad.lcd.clear()
                    er = "Shutting down\ndisplay program"
                    cad.lcd.write(er)
                    slide(er)
                    
                else:
                    cad.lcd.clear()
                    
            elif cad.switches[1].value == 1:
                do_versions()

            elif cad.switches[2].value == 1:
                do_status()

            elif cad.switches[3].value == 1:
                do_netifaces()

            dstart = datetime.now() - timedelta(minutes= 15)
            if cycle == 0:
                try:
                    
                    db = mdb.connect(host= SITE[Station], port = eoss.SQL.port, user= eoss.SQL.user,passwd= eoss.SQL.password, db= eoss.SQL.database)
                    cad.lcd.clear()
                    cad.lcd.write("Station Found:\n{}".format(SITE[Station]))
                    
                    sleep(2)

                except Exception, e:
                    print str(e)
                    cad.lcd.clear()
                    cad.lcd.write("No station at\n{}".format(SITE[Station]))
                    cycle = 1
                sleep(UP/2)
            elif cycle ==1:
                cad.lcd.clear()
                cad.lcd.write("1-Exit   2-Vers\n3-Status 4-Net")

                sleep(2)
            elif cycle == 2:
                cur = db.cursor(mdb.cursors.DictCursor)                    
                cad.lcd.clear()
                cad.lcd.write("Query:\n")
                if eosu.getsetting(db, "TEMP_COUNT", 1) > 0:
                    cad.lcd.write("T")
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
                            
                            t_max = "TMP: {0:.1f} C ".format(out)
                            t_hum = "HUM: {0:.1f} %".format(rel)
                            #get older temp reading
                            a = "SELECT * FROM FEED WHERE TYPE = 3 order by W_TIME limit 0,1"                
                            cur.execute(a)
                            db.commit()
                            row = cur.fetchone()
                            out2 = round(float(row["B1"]) + (float(row["B2"])/ 10),1)
                            if float(row["B6"]) == 1:
                                out2 = out2 * -1
                            
                            cad.lcd.write_custom_bitmap(trenddown_symbol_index)
                        else:
                            cad.lcd.write("-")
                    except Exception, e:
                        print str(e)
                        cad.lcd.write_custom_bitmap(memory_symbol_index)
 
                if eosu.getsetting(db, "PRESSURE_COUNT", 1) > 0:
                    cad.lcd.write("P")
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
                            
                            p_avg = "PRE: {0:.1f} kPa".format(pabs)
                            cad.lcd.write_custom_bitmap(trenddown_symbol_index)
                        else:
                            cad.lcd.write("-")
                    except Exception, e:
                        print str(e)
                        cad.lcd.write_custom_bitmap(memory_symbol_index)
                    
                if eosu.getsetting(db, "SOLAR_COUNT", 1) > 0:
                    cad.lcd.write("S")
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
                            
                            eng = round(rad / 50,3)
                                                              
                            sr_avg = "RAD: {0:.1f} W/m2\n".format(rad)
                            sr_avg = sr_avg + " UV: {0:.1f}\n".format(uv)                         
                            cad.lcd.write_custom_bitmap(trenddown_symbol_index)
                        else:
                            cad.lcd.write("-")
                            
                    except Exception, e:
                        print str(e)
                        cad.lcd.write_custom_bitmap(memory_symbol_index)
                if eosu.getsetting(db, "WIND_COUNT", 1) > 0:
                    cad.lcd.write("W")
                    try:       
                        a = "SELECT * FROM FEED WHERE TYPE = 1 order by W_TIME desc limit 0,1"                                  
                        cur.execute(a)
                        db.commit()
                        row = cur.fetchone()
                        if row is not None:                                
                            spd = round(float(row["B1"]) + (float(row["B2"]) /10),1)
                            gust = round(float(row["B3"]) + (float(row["B4"]) /10),1)
                            avgspd = round(float(row["B5"]) + (float(row["B6"]) /10),1)                           
                            wdir = float(row["B8"] + row["B9"])
                            if spd > 0:
                                w_rose = eosu.wind.windrose(wdir)
                            else:
                                w_rose = "---"                                                

                            wind = "DIR: "+ w_rose + "\n"
                            wind = wind + "SPD: {0:.1f} Kph".format(avgspd)
                            
                            cad.lcd.write_custom_bitmap(trenddown_symbol_index)
                        else:
                            cad.lcd.write("-")
                            
                    except Exception, e:
                        print str(e)
                        cad.lcd.write_custom_bitmap(memory_symbol_index)

                sleep(1)
                cur.close()

                
            
                if eosu.getsetting(db, "TEMP_COUNT", 1) > 0:
                    cad.lcd.clear()
                    cad.lcd.write(t_max)
                    if out > out2:
                        cad.lcd.write_custom_bitmap(trendup_symbol_index)
                    elif out < out2:
                        cad.lcd.write_custom_bitmap(trenddown_symbol_index)
                    cad.lcd.write("\n")
                    cad.lcd.write(t_hum)
                    sleep(UP)

                


                
            elif cycle == 3:

                if eosu.getsetting(db, "PRESSURE_COUNT", 1) > 0:
                    cad.lcd.clear()                               
                    cad.lcd.write(p_avg)
                    if ptrend > 7:
                        cad.lcd.write_custom_bitmap(trendup_symbol_index)
                    elif ptrend > 2 and ptrend < 6:
                        cad.lcd.write_custom_bitmap(trenddown_symbol_index)
                    sleep(UP)

            elif cycle == 4:

                if eosu.getsetting(db, "SOLAR_COUNT", 1) > 0:
                    cad.lcd.clear()                
                    cad.lcd.write(sr_avg)
                    sleep(UP)

            elif cycle == 5:

                if eosu.getsetting(db, "WIND_COUNT", 1) > 0:
                    cad.lcd.clear()
                    cad.lcd.write(wind)
                    sleep(UP)
 
            elif cycle == 6:
                try:
                    a = "SELECT * from ALARM where AM_END > '" + dstart.isoformat() + "'"
                    cur = db.cursor(mdb.cursors.DictCursor)
                    cur.execute(a)
                    db.commit()
                    rows = cur.fetchall()
                    if rows is not None:
                        for row in rows:
                            m = row["MESSAGE"]
                            cad.lcd.clear()
                            cad.lcd.write("ALARM:\n" + m)
                            slide(m)


                except Exception, e:
                    print str(e)
            else:
                cad.lcd.clear()

                
            if cycle < 6:
                cycle = cycle + 1
            else:
                cycle = 1
        
    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print "Exiting Thread..."
        cad.lcd.clear()
        cad.lcd.display_off()
        cad.lcd.backlight_off()


if __name__ == "__main__":
    cad = pifacecad.PiFaceCAD()
    cad.lcd.blink_off()
    cad.lcd.cursor_off()

    if "clear" in sys.argv:
        cad.lcd.clear()
        cad.lcd.display_off()
        cad.lcd.backlight_off()
    else:
        cad.lcd.store_custom_bitmap(temp_symbol_index, temperature_symbol)
        cad.lcd.store_custom_bitmap(memory_symbol_index, memory_symbol)
        cad.lcd.store_custom_bitmap(trendup_symbol_index, trendup_symbol)
        cad.lcd.store_custom_bitmap(trenddown_symbol_index, trenddown_symbol)
        cad.lcd.backlight_on()
        cad.lcd.write("Waiting for\nsystems")
        sleep(1)
        ##wait_for_ip()
        ## Add stations here to monitor
        do_startup()
        SITE.append(eoss.SQL.server)

        
        ## Run routine
        show_sysinfo()       

        sleep(3)
        cad.lcd.clear()
        cad.lcd.display_off()
        cad.lcd.backlight_off()
            
