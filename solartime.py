"""
The :mod:`solartime` module provides the means to calculate dawn, sunrise, solar noon, sunset,
and dusk, at a specific latitude/longitude.

The module provides one main class, :class:`SolarTime`.

:class:`SolarTime`
    * Calculates events in the UTC timezone.

Example usage ::

    >>> from datetime import date
    >>> from pytz import timezone
    >>> from solartime import SolarTime
    >>> today = date(2014, 1, 19)
    >>> localtz = timezone('US/Eastern')
    >>> lat, lon = 38.0, -79.0
    >>> sun = SolarTime()
    >>> schedule = sun.sun_utc(today, lat, lon)
    >>> sunset = schedule['sunset'].astimezone(localtz)
    >>> print(sunset)
    2014-01-19 17:24:43-05:00

"""

import datetime
from math import cos, sin, tan, acos, asin, floor, radians, degrees

try:
    import pytz
except ImportError:
    raise ImportError('The solartime module requires the pytz module to be available.')

try:
    basestring  # Python 2/3 compatibility
except NameError:
    basestring = str


__all__ = ['SolarTime', 'SolarError']

__version__ = '0.1b1'
__license__ = 'Apache 2.0'
__author__  = 'Simon Kennedy <code@sffjunkie.co.uk>, David Riggs <driggs@myotisoft.com>'


class SolarError(Exception):
    pass


class SolarTime(object):

    def __init__(self, solar_depression=6):
        """Create a SolarTime calculator.

        :param solar_depression:  Number of degrees the sun must be below the horizon for dawn/dusk calculation
        :type number or str:  Either number of degrees, or one of 'civil', 'nautical', 'astronomical'
        """

        self._depression = 6
        self.solar_depression = solar_depression  # Set default depression in degrees

    @property
    def solar_depression(self):
        """The number of degrees the sun must be below the horizon for the
        dawn/dusk calc.

        Can either be set as a number of degrees below the horizon or as
        one of the following strings

        ============= =======
        String        Degrees
        ============= =======
        civil            6.0
        nautical        12.0
        astronomical    18.0
        ============= =======
        """
        return self._depression

    @solar_depression.setter
    def solar_depression(self, depression):
        if isinstance(depression, basestring):
            try:
                self._depression = {
                    'civil': 6,
                    'nautical': 12,
                    'astronomical': 18}[depression]
            except:
                raise KeyError("solar_depression must be either a number or one of 'civil', 'nautical' or 'astronomical'")
        else:
            self._depression = float(depression)

    def sun_utc(self, date, latitude, longitude):
        """Calculate all the info for the sun at once.

        :param date:       Date to calculate for.
        :type date:        :class:`datetime.date`
        :param latitude:   Latitude - Northern latitudes should be positive
        :type latitude:    float
        :param longitude:  Longitude - Eastern longitudes should be positive
        :type longitude:   float

        :rtype:
            Dictionary with keys ``dawn``, ``sunrise``, ``noon``, ``sunset`` and ``dusk``
        """

        return {
            'dawn':    self.dawn_utc(date, latitude, longitude),
            'sunrise': self.sunrise_utc(date, latitude, longitude),
            'noon':    self.solar_noon_utc(date, longitude),
            'sunset':  self.sunset_utc(date, latitude, longitude),
            'dusk':    self.dusk_utc(date, latitude, longitude)
        }

    def dawn_utc(self, date, latitude, longitude):
        """Calculate dawn time in the UTC timezone.

        :param date:       Date to calculate for.
        :type date:        datetime.date
        :param latitude:   Latitude - Northern latitudes should be positive
        :type latitude:    float
        :param longitude:  Longitude - Eastern longitudes should be positive
        :type longitude:   float

        :rtype: date/time in UTC timezone
        """

        try:
            return self._calc_time(date, latitude, longitude, self._depression)
        except:
            raise SolarError('Sun remains below the horizon on this day, at this location.')

    def sunrise_utc(self, date, latitude, longitude):
        """Calculate sunrise time in the UTC timezone.

        :param date:       Date to calculate for.
        :type date:        datetime.date
        :param latitude:   Latitude - Northern latitudes should be positive
        :type latitude:    float
        :param longitude:  Longitude - Eastern longitudes should be positive
        :type longitude:   float

        :rtype: date/time in UTC timezone
        """

        try:
            return self._calc_time(date, latitude, longitude, 0.833)
        except:
            raise SolarError('Sun remains below the horizon on this day, at this location.')

    def solar_noon_utc(self, date, longitude):
        """Calculate solar noon time in the UTC timezone.

        :param date:       Date to calculate for.
        :type date:        datetime.date
        :param latitude:   Latitude - Northern latitudes should be positive
        :type latitude:    float
        :param longitude:  Longitude - Eastern longitudes should be positive
        :type longitude:   float

        :rtype: date/time in UTC timezone
        """

        julianday = self._julianday(date)

        newt = self._jday_to_jcentury(julianday + 0.5 + -longitude / 360.0)

        eqtime = self._eq_of_time(newt)
        timeUTC = 720.0 + (-longitude * 4.0) - eqtime

        timeUTC /= 60.0
        hour = int(timeUTC)
        minute = int((timeUTC - hour) * 60)
        second = int((((timeUTC - hour) * 60) - minute) * 60)

        if second > 59:
            second -= 60
            minute += 1
        elif second < 0:
            second += 60
            minute -= 1

        if minute > 59:
            minute -= 60
            hour += 1
        elif minute < 0:
            minute += 60
            hour -= 1

        if hour > 23:
            hour -= 24
            date += datetime.timedelta(days=1)
        elif hour < 0:
            hour += 24
            date -= datetime.timedelta(days=1)

        return datetime.datetime(date.year, date.month, date.day, hour, minute, second, tzinfo=pytz.utc)

    def sunset_utc(self, date, latitude, longitude):
        """Calculate sunset time in the UTC timezone.

        :param date:       Date to calculate for.
        :type date:        datetime.date
        :param latitude:   Latitude - Northern latitudes should be positive
        :type latitude:    float
        :param longitude:  Longitude - Eastern longitudes should be positive
        :type longitude:   float

        :rtype: date/time in UTC timezone
        """

        try:
            return self._calc_time(date, latitude, longitude, -0.833)
        except:
            raise SolarError('Sun remains below the horizon on this day, at this location.')

    def dusk_utc(self, date, latitude, longitude):
        """Calculate dusk time in the UTC timezone.

        :param date:       Date to calculate for.
        :type date:        datetime.date
        :param latitude:   Latitude - Northern latitudes should be positive
        :type latitude:    float
        :param longitude:  Longitude - Eastern longitudes should be positive
        :type longitude:   float

        :rtype: date/time in UTC timezone
        """

        try:
            return self._calc_time(date, latitude, longitude, - self._depression)
        except:
            raise SolarError('Sun remains below the horizon on this day, at this location.')

    def _julianday(self, date, timezone=None):
        day = date.day
        month = date.month
        year = date.year

        if timezone is not None:
            offset = timezone.localize(datetime.datetime(year, month, day)).utcoffset()
            offset = offset.total_seconds() / 1440.0
            day += offset + 0.5

        if month <= 2:
            year -= 1
            month += 12

        A = floor(year / 100.0)
        B = 2 - A + floor(A / 4.0)

        jd = floor(365.25 * (year + 4716)) + floor(30.6001 * (month + 1)) + day - 1524.5
        if jd > 2299160.4999999:
            jd += B

        return jd

    def _jday_to_jcentury(self, julianday):
        return (julianday - 2451545.0) / 36525.0

    def _jcentury_to_jday(self, juliancentury):
        return (juliancentury * 36525.0) + 2451545.0

    def _mean_obliquity_of_ecliptic(self, juliancentury):
        seconds = 21.448 - juliancentury * (46.815 + juliancentury * (0.00059 - juliancentury * 0.001813))
        return 23.0 + (26.0 + (seconds / 60.0)) / 60.0

    def _obliquity_correction(self, juliancentury):
        e0 = self._mean_obliquity_of_ecliptic(juliancentury)
        omega = 125.04 - 1934.136 * juliancentury
        return e0 + 0.00256 * cos(radians(omega))

    def _geom_mean_long_sun(self, juliancentury):
        l0 = 280.46646 + juliancentury * (36000.76983 + 0.0003032 * juliancentury)
        return l0 % 360.0

    def _eccentrilocation_earth_orbit(self, juliancentury):
        return 0.016708634 - juliancentury * (0.000042037 + 0.0000001267 * juliancentury)

    def _geom_mean_anomaly_sun(self, juliancentury):
        return 357.52911 + juliancentury * (35999.05029 - 0.0001537 * juliancentury)

    def _eq_of_time(self, juliancentury):
        epsilon = self._obliquity_correction(juliancentury)
        l0 = self._geom_mean_long_sun(juliancentury)
        e = self._eccentrilocation_earth_orbit(juliancentury)
        m = self._geom_mean_anomaly_sun(juliancentury)

        y = tan(radians(epsilon) / 2.0)
        y = y * y

        sin2l0 = sin(2.0 * radians(l0))
        sinm = sin(radians(m))
        cos2l0 = cos(2.0 * radians(l0))
        sin4l0 = sin(4.0 * radians(l0))
        sin2m = sin(2.0 * radians(m))

        Etime = y * sin2l0 - 2.0 * e * sinm + 4.0 * e * y * sinm * cos2l0 - 0.5 * y * y * sin4l0 - 1.25 * e * e * sin2m
        return degrees(Etime) * 4.0

    def _sun_eq_of_center(self, juliancentury):
        m = self._geom_mean_anomaly_sun(juliancentury)

        mrad = radians(m)
        sinm = sin(mrad)
        sin2m = sin(mrad + mrad)
        sin3m = sin(mrad + mrad + mrad)

        c = sinm * (1.914602 - juliancentury * (0.004817 + 0.000014 * juliancentury)) + sin2m * (0.019993 - 0.000101 * juliancentury) + sin3m * 0.000289
        return c

    def _sun_true_long(self, juliancentury):
        l0 = self._geom_mean_long_sun(juliancentury)
        c = self._sun_eq_of_center(juliancentury)
        return l0 + c

    def _sun_apparent_long(self, juliancentury):
        O = self._sun_true_long(juliancentury)

        omega = 125.04 - 1934.136 * juliancentury
        return O - 0.00569 - 0.00478 * sin(radians(omega))

    def _sun_declination(self, juliancentury):
        e = self._obliquity_correction(juliancentury)
        lambd = self._sun_apparent_long(juliancentury)

        sint = sin(radians(e)) * sin(radians(lambd))
        return degrees(asin(sint))

    def _hour_angle(self, latitude, solar_dec, solar_depression):
        latRad = radians(latitude)
        sdRad = radians(solar_dec)

        HA = (acos(cos(radians(90 + solar_depression)) / (cos(latRad) * cos(sdRad)) - tan(latRad) * tan(sdRad)))
        return HA

    def _calc_time(self, date, latitude, longitude, depression):
        julianday = self._julianday(date)

        if latitude > 89.8:
            latitude = 89.8

        if latitude < -89.8:
            latitude = -89.8

        t = self._jday_to_jcentury(julianday)
        eqtime = self._eq_of_time(t)
        solarDec = self._sun_declination(t)

        hourangle = -self._hour_angle(latitude, solarDec, 0.833)

        delta = -longitude - degrees(hourangle)
        timeDiff = 4.0 * delta
        timeUTC = 720.0 + timeDiff - eqtime

        newt = self._jday_to_jcentury(self._jcentury_to_jday(t) + timeUTC / 1440.0)
        eqtime = self._eq_of_time(newt)
        solarDec = self._sun_declination(newt)

        if depression < 0:
            depression = abs(depression)
            hourangle = -self._hour_angle(latitude, solarDec, depression)
        else:
            hourangle = self._hour_angle(latitude, solarDec, depression)

        delta = -longitude - degrees(hourangle)
        timeDiff = 4 * delta
        timeUTC = 720 + timeDiff - eqtime

        timeUTC /= 60.0
        hour = int(timeUTC)
        minute = int((timeUTC - hour) * 60)
        second = int((((timeUTC - hour) * 60) - minute) * 60)

        if second > 59:
            second -= 60
            minute += 1
        elif second < 0:
            second += 60
            minute -= 1

        if minute > 59:
            minute -= 60
            hour += 1
        elif minute < 0:
            minute += 60
            hour -= 1

        if hour > 23:
            hour -= 24
            date += datetime.timedelta(days=1)
        elif hour < 0:
            hour += 24
            date -= datetime.timedelta(days=1)

        return datetime.datetime(date.year, date.month, date.day, hour, minute, second, tzinfo=pytz.utc)
