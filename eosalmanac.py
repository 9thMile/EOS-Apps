#
#    Copyright (c) 2009, 2011, 2012 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
#    $Revision: 1561 $
#    $Author: tkeffer $
#    $Date: 2013-10-21 11:51:51 -0400 (Mon, 21 Oct 2013) $
#
"""Almanac data

This module can optionally use PyEphem, which offers high quality
astronomical calculations. See http://rhodesmill.org/pyephem. """
import paho.mqtt.publish as publish
from datetime import datetime, timedelta, tzinfo
import time
import sys
import math
import MySQLdb as mdb
import Moon
import Sun
import eossql as eoss
import eosutils as eosu
import eospush as eosp

class Station:
    Name = "EOS_Station"
    Broker_Address = ''
    Broker_Port = ''
    Broker_USN = ''
    Broker_PWD = ''    
# NB: In order to avoid an 'autocall' bug in Cheetah versions before 2.1,
# this class must not be a "new-style" class.
class Almanac():
    """Almanac data.
    
    ATTRIBUTES.
    
    As a minimum, the following attributes are available:
    
        sunrise: Time (local) upper limb of the sun rises above the horizon, formatted using the format 'timeformat'.
        sunset: Time (local) upper limb of the sun sinks below the horizon, formatted using the format 'timeformat'.
        moon_phase: A description of the moon phase(eg. "new moon", Waxing crescent", etc.)
        moon_fullness: Percent fullness of the moon (0=new moon, 100=full moon)

    """
    
    def __init__(self):
        """Initialize an instance of Almanac
        """
        self.time_ts      = time.time()
        self.time_djd     = timestamp_to_djd(self.time_ts)
        self.lat          = float(eosu.getsetting(db, "LATITUDE", 0))
        self.lon          = float(eosu.getsetting(db, "LONGITUDE", 0))
        self.altitude     = float(eosu.getsetting(db, "ALTITUDE", 1))
        self.moon_phases  = Moon.moon_phases


        (y,m,d) = time.localtime(self.time_ts)[0:3]
        (self.moon_index, self.moon_fullness) = Moon.moon_phase(y, m, d)
        self.moon_phase = self.moon_phases[int(self.moon_index/3)]
            

        
        # No ephem package. Use the weeutil algorithms, which supply a minimum of functionality
        (sunrise_utc, sunset_utc) = Sun.sunRiseSet(y, m, d, self.lon, self.lat)
        # The above function returns its results in UTC hours. Convert
        # to a local time tuple
        sunrise_tt = eosu.utc_to_local_tt(y, m, d, sunrise_utc)
        sunset_tt  = eosu.utc_to_local_tt(y, m, d, sunset_utc)
        self.sunrise = time.strftime("%H:%M:%S", sunrise_tt)
        self.sunset  = time.strftime("%H:%M:%S", sunset_tt)
        
        self.solar_max = round(Sun.get_max_solar_flux(self.lat, y, m, d),0)
        self.solar_alt = round(Sun.solar_altitude(self.lat, y, m, d),0)
        self.daylength = round(Sun.dayLength(y, m, d, self.lon, self.lat),2)        

def main():
    global db
    db = mdb.connect(host= eoss.SQL.server, port = eoss.SQL.port, user= eoss.SQL.user,passwd= eoss.SQL.password, db= eoss.SQL.database)
    ## Set up a local cursor to hold data and execute statments
    cur = db.cursor(mdb.cursors.DictCursor)
    almanac = Almanac()
    (y,m,d) = time.localtime(almanac.time_ts)[0:3]
    dend = datetime(y, m, d, 0, 0, 0)
    we_date = dend.strftime("%Y-%m-%d")
    a = "DELETE from ALMANAC where WE_DATE = '%s'" % we_date
    cur.execute(a)
    db.commit()
    values = "'" + we_date + "','" + almanac.sunrise + "','" + almanac.sunset + "'," + str(almanac.solar_max) + "," + str(almanac.solar_alt) + "," + str(almanac.daylength) + ","+ str(almanac.moon_index) + ",'" + str(almanac.moon_phase) + "'," + str(almanac.moon_fullness)
    a = "INSERT INTO ALMANAC VALUES(%s)" %values
    cur.execute(a)
    db.commit()
    eosp.remotealmanac(db, eosu.getsetting(db, "REM_ID",0), we_date, almanac)
    if eosu.getsetting(db, "BROKER_ADDRESS",0) <> "":
        Station.Name  = eosu.getsetting(db, "NAME", 0)
        Station.Broker_Address = eosu.getsetting(db, "BROKER_ADDRESS", 0)
        Station.Broker_Port = eosu.getsetting(db, "BROKER_PORT", 0)
        Station.Broker_USN = eosu.getsetting(db, "BROKER_USN", 0)
        Station.Broker_PWD = eosu.getsetting(db, "BROKER_PWD", 0)
        auth = {'username':Station.Broker_USN,'password':Station.Broker_PWD}
        publish.single(topic= Station.Name + '/Almanac/Sun/Rise',payload=almanac.sunrise,qos=0,retain=True, hostname=Station.Broker_Address,port=Station.Broker_Port,client_id='EOS_Station',auth=auth)
        time.sleep(15)
        publish.single(topic= Station.Name + '/Almanac/Sun/Set',payload=almanac.sunset,qos=0,retain=True, hostname=Station.Broker_Address,port=Station.Broker_Port,client_id='EOS_Station',auth=auth)
        time.sleep(15)
        publish.single(topic= Station.Name + '/Almanac/Sun/SolarMax',payload=almanac.solar_max,qos=0,retain=True, hostname=Station.Broker_Address,port=Station.Broker_Port,client_id='EOS_Station',auth=auth)
        time.sleep(15)
        publish.single(topic= Station.Name + '/Almanac/Sun/SolarAlt',payload=almanac.solar_alt,qos=0,retain=True, hostname=Station.Broker_Address,port=Station.Broker_Port,client_id='EOS_Station',auth=auth)
        time.sleep(15)
        publish.single(topic= Station.Name + '/Almanac/Moon/Phase',payload=almanac.moon_phase,qos=0,retain=True, hostname=Station.Broker_Address,port=Station.Broker_Port,client_id='EOS_Station',auth=auth)
        time.sleep(15)
        publish.single(topic= Station.Name + '/Almanac/DayLength',payload=almanac.daylength,qos=0,retain=True, hostname=Station.Broker_Address,port=Station.Broker_Port,client_id='EOS_Station',auth=auth)
        time.sleep(15)
        
    
##
##    print a
##    print almanac.sunrise
##    print almanac.sunset
##    print almanac.solar_max
##    print almanac.solar_alt
##    print almanac.daylength
##    print almanac.moon_phase
##    print almanac.moon_index
##    print almanac.moon_fullness
##    print we_date
##    


def timestamp_to_djd(time_ts):
    """Convert from a unix time stamp to the number of days since 12/31/1899 12:00 UTC
    (aka "Dublin Julian Days")"""
    # The number 25567.5 is the start of the Unix epoch (1/1/1970). Just add on the
    # number of days since then
    return 25567.5 + time_ts/86400.0
    
def djd_to_timestamp(djd):
    """Convert from number of days since 12/31/1899 12:00 UTC ("Dublin Julian Days") to unix time stamp"""
    return (djd-25567.5) * 86400.0


    
if __name__ == '__main__':
    main()
    
