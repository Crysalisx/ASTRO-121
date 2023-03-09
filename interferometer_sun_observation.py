import threading
import numpy as np
import astropy as ap
from astropy.coordinates import EarthLocation
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.time import Time
import matplotlib as plt
import datetime 
from datetime import timezone
import math
import time
import ugradio

def get_julian_datetime(date):
    """
    Convert a datetime object into julian float.
    Args:
        date: datetime-object of date in question

    Returns: float - Julian calculated datetime.
    Raises: 
        TypeError : Incorrect parameter type
        ValueError: Date out of range of equation
    """

    # Ensure correct format
    if not isinstance(date, datetime.datetime):
        raise TypeError('Invalid type for parameter "date" - expecting datetime')
    elif date.year < 1801 or date.year > 2099:
        raise ValueError('Datetime must be between year 1801 and 2099')

    # Perform the calculation
    julian_datetime = 367 * date.year - int((7 * (date.year + int((date.month + 9) / 12.0))) / 4.0) + int(
        (275 * date.month) / 9.0) + date.day + 1721013.5 + (
                          date.hour + date.minute / 60.0 + date.second / math.pow(60,
                                                                                  2)) / 24.0 - 0.5 * math.copysign(
        1, 100 * date.year + date.month - 190002.5) + 0.5

    return julian_datetime

# Get LST. This part is run first because it takes a long time for some reason.
observing_location = EarthLocation(lat=37.8732*u.deg, lon=237.7427*u.deg)
observing_time = Time(datetime.datetime.utcnow(), scale='utc', location=observing_location)
LST = observing_time.sidereal_time('mean')

#Get regular date/time
current_time = datetime.datetime.now()

#Get UTC time
dt = datetime.datetime.now(timezone.utc)
utc_time = dt.replace(tzinfo=timezone.utc)
utc_timestamp = utc_time.timestamp()


print('The current date (YYYY-MM-DD) and time (HH:MM:SS) is',current_time)
print('')
print('Current UTC time is', utc_timestamp)
print('')
print('The current Julian Date is', get_julian_datetime(dt))
print('')
print('The current Local Sidereal Time is',LST)
print('')

def get_sun_coords(ifm):
    get_julian_time(datetime.datetime.now(timezone.utc))
    raw_sun_pos = ugradio.coords.sunpos(get_julian_time)
    sun_pos = ugradio.coord.get_altaz(raw_sun_pos[0],raw_sun_pos[1], get_julian_time, observing_location[0], observing_location[0], 0)
    ifm.point(sun_pos[0], sun_pos[1])
    
def point_update(ifm):
    while True:
        try:
            get_sun_coords(ifm)
        except:
            print('Whoopsie with position')
        time.sleep(2)

def get_data(spec):
    global unsaved_data
    while True:
        try:
            new = spec.read_data()
            np.append(new)
        except:
            np.append(np.empty)
        time.sleep(30)

def save_data():
    global unsaved_data
    while True:
        if (unsaved_data.size() >=10):
            try:
                data = np.pop(unsaved_data)
                np.savez('/femmefataledata/quetzaltime'+str(datetime.datetime.now(timezone.utc))+'.npz', data)
            except:
                print('could not save at '+str(datetime.datetime.now(timezone.utc)))
        time.sleep(10)
        
        
def wrapup():
    times = get_julian_time(datetime.datetime.now(timezone.utc))
       while (times < 2460013.25694): #checks if the sun's down yet
            time.sleep(120)
            times = get_julian_time(datetime.datetime.now(timezone.utc))
       

unsaved_data = np.empty()
ifm = ugradio.interf.Interferometer()
spec = snap_spec.snap.UGRadioSnap()
spec.initialize(mode='corr')
get_sun_coords()
position_update = threading.Thread(target = point_update())
data_capture = threading.Thread(target = get_data())
save_data = threading.Thread(target = save_data())
position_update.start()
data_capture.start()
save_data.start()
wrap = threading.Thread(target = wrapup())
wrap.start()
wrap.join()
