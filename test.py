import unittest
from datetime import date, datetime

from pytz import timezone

from solartime import SolarTime


class SolarTimeTest(unittest.TestCase):
    """
    Compare calculated times for a canned location to US Navy's online calculator.

    http://aa.usno.navy.mil/rstt/onedaytable?form=2&ID=AA&year=2015&month=1&day=20&place=%28no+name+given%29&lon_sign=-1&lon_deg=79&lon_min=&lat_sign=1&lat_deg=38&lat_min=&tz=5&tz_sign=-1

    FIXME: all our calculations differ from the above reference by as much as 00:04:00!
    """

    def setUp(self):
        self.sun = SolarTime('civil')
        self.lat, self.lon = 38.0, -79.0
        self.today = date(2015, 01, 20)
        self.localtz = timezone('US/Eastern')
        self.schedule = self.sun.sun_utc(self.today, self.lat, self.lon)

    def test_sunrise(self):
        sunrise = self.schedule['sunrise'].astimezone(self.localtz)
        expected_sunrise = datetime(2015, 01, 20, 07, 29, tzinfo=self.localtz)
        self.assertEqual(sunrise, expected_sunrise, 'Sunrise is %s from expected time' % (sunrise - expected_sunrise))

    def test_sunset(self):
        sunset = self.schedule['sunset'].astimezone(self.localtz)
        expected_sunset = datetime(2015, 01, 20, 17, 26, tzinfo=self.localtz)
        self.assertEqual(sunset, expected_sunset, 'Sunset is %s from expected time' % (sunset - expected_sunset))

    def test_solarnoon(self):
        noon = self.schedule['noon'].astimezone(self.localtz)
        expected_noon = datetime(2015, 01, 20, 12, 27, 00, tzinfo=self.localtz)
        self.assertEqual(noon, expected_noon, 'Solar noon is %s from expected time' % (noon - expected_noon))

    def test_dawn(self):
        dawn = self.schedule['dawn'].astimezone(self.localtz)
        expected_dawn = datetime(2015, 01, 20, 07, 00, tzinfo=self.localtz)  # end of civil twilight
        self.assertEqual(dawn, expected_dawn, 'Dawn is %s from expected time' % (dawn - expected_dawn))

    def test_dusk(self):
        dusk = self.schedule['dusk'].astimezone(self.localtz)
        expected_dusk = datetime(2015, 01, 20, 17, 54, tzinfo=self.localtz)  # end of civil twilight
        self.assertEqual(dusk, expected_dusk, 'Dusk is %s from expected time' % (dusk - expected_dusk))
