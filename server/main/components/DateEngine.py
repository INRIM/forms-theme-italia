import locale
import datetime
from collections import namedtuple
from datetime import date, datetime, timedelta

import pytz
import locale

try:
    locale.setlocale(locale.LC_ALL, "it_IT")
except:
    pass


class DateEngine():

    def __init__(self,
                 SERVER_DT_MASK="%Y-%m-%d",
                 SERVER_DTTIME_MASK="%Y-%m-%d %H:%M:%S",
                 UI_DATE_MASK="%d/%m/%Y",
                 REPORT_DATE_MASK="%d-%m-%Y",
                 UI_DATETIME_MASK="%d/%m/%Y %H:%M:%S",
                 TZ="Europe/Rome"
                 ):
        super().__init__()
        self.client_date_mask = UI_DATE_MASK
        self.client_datetime_mask = UI_DATETIME_MASK
        self.report_date_mask = REPORT_DATE_MASK
        self.server_date_mask = SERVER_DT_MASK
        self.server_datetime_mask = SERVER_DTTIME_MASK
        self.tz = pytz.timezone(str(pytz.timezone(str(TZ))))

    def get_date_from_server(self, date_to_parse) -> date:
        parsed = datetime.strptime(
            date_to_parse, self.server_date_mask).date()
        return parsed

    def ui_date_to_server_date_str(self, date_to_parse) -> str:
        parsed = datetime.strptime(
            date_to_parse, self.client_date_mask).date().strftime(self.server_date_mask)
        return parsed

    def server_date_to_ui_date_str(self, date_to_parse) -> str:
        parsed = datetime.strptime(
            date_to_parse, self.server_date_mask).date().strftime(self.client_date_mask)
        return parsed

    def ui_datetime_to_server_datetime_str(self, date_to_parse) -> str:
        parsed = datetime.strptime(
            date_to_parse, self.client_datetime_mask).strftime(self.server_datetime_mask)
        return parsed

    def server_datetime_to_ui_datetime_str(self, date_to_parse) -> str:
        parsed = datetime.strptime(
            date_to_parse, self.server_datetime_mask).strftime(self.client_datetime_mask)
        return parsed

    def get_server_datetime_now(self) -> str:
        return datetime.now().astimezone(self.tz).strftime(self.server_datetime_mask)

    def get_server_datetime_now_tz(self) -> str:
        return datetime.now().astimezone(
            self.tz).strftime(self.server_datetime_mask)

    def strdate_ui_to_date(self, date_to_parse) -> date:
        date_to_parse = datetime.strptime(
            date_to_parse, self.client_date_mask).date()
        return date_to_parse

    def strdatetime_ui_to_datetime(self, datetime_to_parse) -> datetime:
        date_to_parse = datetime.strptime(
            datetime_to_parse, self.client_date_mask)
        return date_to_parse

    def strdate_serve_to_date(self, date_to_parse) -> date:
        date_to_parse = datetime.strptime(
            date_to_parse, self.server_date_mask).date()
        return date_to_parse

    def strdatetime_server_to_datetime(self, datetime_to_parse):
        date_to_parse = datetime.strptime(
            datetime_to_parse, self.server_date_mask)
        return date_to_parse

    def stratetime_server_tz(self, datetime_to_parse):
        date_to_parse = datetime.strptime(
            datetime_to_parse, self.server_date_mask)
        return date_to_parse

    def datetimestr_server_tz_str(self, datetime_to_parse):
        date_to_parse = datetime.strptime(
            datetime_to_parse, self.server_date_mask).astimezone(
            self.tz).strftime(self.server_date_mask)
        return date_to_parse

    def datetimestr_to_ui_datetime_tz(self, datetime_to_parse):
        res = ''
        if datetime_to_parse:
            date_to_parse = datetime.strptime(
                datetime_to_parse, self.server_datetime_mask).astimezone(self.tz)
            res = date_to_parse.strftime(self.client_datetime_mask)
        return res

    def get_date_delta_from_today(self, deltat):
        return date.today() + timedelta(deltat)

    def gen_date_delta_from_today_masked(self, deltat, mask):
        return (date.today() + timedelta(deltat)).strftime(mask)

    def gen_date_min_max_gui(self, min_day_delata_date_from=1, max_day_delata_date_to=5):
        min = self.gen_date_delta_from_today_masked(min_day_delata_date_from, self.client_date_mask)
        max = self.gen_date_delta_from_today_masked(max_day_delata_date_to, self.client_date_mask)
        return min, max

    def gen_date_min_max(self, min_day_delata_date_from=1, max_day_delata_date_to=5):
        min = self.gen_date_delta_from_today_masked(min_day_delata_date_from, self.server_date_mask)
        max = self.gen_date_delta_from_today_masked(max_day_delata_date_to, self.server_date_mask)
        return min, max

    def gen_date_from_to_gui_dict(self, min_day_delata_date_from=1, max_day_delata_date_to=5):
        dtmin, dtmax = self.gen_date_min_max_gui(min_day_delata_date_from, max_day_delata_date_to)
        res = {
            "date_from": dtmin,
            "date_to": dtmax,
        }
        return res

    def gen_date_from_to_dict(self, min_day_delata_date_from=1, max_day_delata_date_to=5):
        dtmin, dtmax = self.gen_date_min_max(min_day_delata_date_from, max_day_delata_date_to)
        res = {
            "date_from": dtmin,
            "date_to": dtmax,
        }
        return res

    def get_date_start_stop_by_delta(self, deltad, mask):
        return {
            'date_start': self.gen_date_delta_from_today_masked(int(deltad), mask),
            'date_stop': self.gen_date_delta_from_today_masked(int(deltad), mask)
        }

    def is_today_or_less(self, datestr):
        dtload = self.get_date_from_server(datestr)
        return dtload <= date.today()

    def is_less_today(self, datestr):
        dtload = self.get_date_from_server(datestr)
        return dtload < date.today()

    def checkDateFromToClient(self, date_from, date_to):
        dti = datetime.strptime(date_from, self.client_date_mask)
        dtf = datetime.strptime(date_to, self.client_date_mask)
        if dti < dtf:
            return True
        else:
            return False

    def checkLimitMaxClientDate(self, date_text, date_limit):
        dt = datetime.strptime(date_text, self.client_date_mask)
        dtLimit = datetime.strptime(date_limit, self.client_date_mask)
        if dt <= dtLimit:
            return True
        else:
            return False

    def checkLimitMinClientDate(self, date_text, date_limit):
        dt = datetime.strptime(date_text, self.client_date_mask)
        dtLimit = datetime.strptime(date_limit, self.client_date_mask)
        if dt >= dtLimit:
            return True
        else:
            return False

    def afterTodayClientDate(self, date_text):
        dt = datetime.strptime(date_text, self.client_date_mask).date()
        dtLimit = date.today()
        if dt >= dtLimit:
            return True
        else:
            return False

    def validateClientDate(self, date_text):
        try:
            datetime.strptime(date_text, self.client_date_mask)
            return True
        except ValueError:
            return False

    def validateServerDate(self, date_text):
        try:
            datetime.strptime(date_text, self.server_date_mask)
            return True
        except ValueError:
            return False

    def default_date(self, o):
        if isinstance(o, (date, datetime)):
            return o.strftime(self.client_date_mask)

    def get_tooday_ui(self):
        return self.default_date(date.today())

    def check_dates_overlap(self, list_date1, list_date2):
        Range = namedtuple('Range', ['start', 'end'])
        r1 = Range(start=list_date1[0], end=list_date1[1])
        r2 = Range(start=list_date2[0], end=list_date2[1])
        latest_start = max(r1.start, r2.start)
        earliest_end = min(r1.end, r2.end)
        delta = (earliest_end - latest_start).days + 1
        overlap = max(0, delta)
        return overlap
