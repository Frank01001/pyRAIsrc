import datetime

months_str = ['Invalid', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
              'October', 'November', 'December']
days_of_week = ['Invalid', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

'''
Data structure containing all information encoded in an SRC time signal
'''
class InformationBlock:

    '''Basic Init'''
    def __init__(self):
        self.hour = 0
        self.minutes = 0
        self.time_zone = 0
        self.month = 0
        self.day = 0
        self.day_of_week = 0
        self.year = 0
        self.next_tz_change = 0
        self.leap_second = 0

    '''
    Directly sets the hour and minutes value of the object
    warning: no check on consistency (0 <= hours < 24, 0 <= minutes < 60)
    '''
    def set_time(self, hour, minutes):
        self.hour = hour
        self.minutes = minutes

    '''
    Directly sets the date parameters of the object
    warning: no check on consistency (e.g. day of the week, inexistent days, etc)
    '''
    def set_date(self, day, month, year, day_of_week):
        self.day = day
        self.month = month
        self.year = year
        # 20th century
        if year > datetime.date.today().year - 2000:
            self.year += 1900
        # 21st century
        else:
            self.year += 2000

        self.day_of_week = day_of_week

    '''
    Sets the time zone tag as a string given the value of the OE bit
    '''
    def set_time_zone(self, oe_bit):
        self.time_zone = 'CEST' if oe_bit is True else 'CET'

    '''
    Stores the information on the next DST change
    '''
    def set_next_time_zone_change(self, next_tz_change):
        self.next_tz_change = next_tz_change if next_tz_change < 7 else -1

    '''
    Stores the information on a possible imminent leap second
    '''
    def set_leap_second(self, leap_second):
        self.leap_second = leap_second

    '''
    Prints all relevant information from the InformationBlock
    - verbose mode prints ALL information
    '''
    def print_info(self, verbose = False):
        print('-------------- Rai SRC Frame Information Begin -----------------')
        print('Date: {} {} {} {}'.format(days_of_week[self.day_of_week],
                                         months_str[self.month],
                                         self.day,
                                         self.year))
        print('Time: {:02d}:{:02d}'.format(self.hour, self.minutes))
        print('Current time zone: {}'.format(self.time_zone))

        if self.next_tz_change > 0:
            print('     {} days to Daylight Saving Time change'.format(self.next_tz_change))
        elif verbose is True:
            print('     next Daylight Saving Time change is more than 7 days away')

        if self.leap_second > 0:
            print('Leap Second: One second delay at the end of the month')
        elif self.leap_second < 0:
            print('Leap Second: One second advance at the end of the month')
        elif verbose is True:
            print('No Leap Second within the current month')

        print('------------------------- End of Frame -------------------------')

    '''
    Returns a datetime object with the relevant information from the InformationBlock object
    '''
    def to_datetime(self):
        delta = datetime.timedelta(hours=1) if self.time_zone == 'CET' else datetime.timedelta(hours=2)
        tz = datetime.timezone(delta)
        buffer = datetime.datetime(self.year, self.month, self.day, self.hour, self.minutes, 0, 0, tzinfo=tz)
        return buffer

    '''
    Returns an InformationBlock object with information from a datetime object
    - information on next DST change and leap second have to be manually added or left to default
    '''
    @staticmethod
    def from_datetime(dt : datetime.datetime, time_zone, next_tz_change=-1, leap_second=0):
        buffer = InformationBlock()
        buffer.hour = dt.hour
        buffer.minutes = dt.minute
        buffer.day = dt.day
        buffer.month = dt.month
        buffer.year = dt.year
        buffer.day_of_week = dt.weekday() + 1
        buffer.time_zone = time_zone
        buffer.leap_second = leap_second
        buffer.next_tz_change = next_tz_change
        return buffer

