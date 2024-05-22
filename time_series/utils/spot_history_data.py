import os
from datetime import date, timedelta
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError
from api_gateway.settings.config import DJANGO_DEBUG, DJANGO_TESTING


def backfill_spot_history_data(sender, **kwargs):
    if DJANGO_TESTING or not DJANGO_DEBUG:
        print("Skipping spot history data backfill")
        return

    try:
        with connection.cursor() as cursor:
            print("Checking if the table is up to date")
            cursor.execute(
                "SELECT MAX(date), AVG(rate), currency FROM spot_history_data GROUP BY currency"
            )
            rows_inserted = 0
            for item in cursor.fetchall():
                if count_work_days(item[0], date.today()) > 0:
                    sql = ""
                    next_day = get_next_work_day(item[0])
                    while next_day <= date.today():
                        sql = (
                            sql
                            + f"INSERT INTO public.spot_history_data(date, currency, rate) VALUES ('{next_day}', '{item[2]}', {item[1]});"
                        )
                        next_day = get_next_work_day(next_day)
                        rows_inserted += 1
                    cursor.execute(sql)
            print(f"Rows inserted {rows_inserted}")

    except (OperationalError, ProgrammingError) as e:
        print("Table does not exist or another error: ", e)


def count_work_days(start_date: date, end_date: date):
    WEEKDAY_FRIDAY = 4
    """
    Math function to get workdays between 2 dates.
    Can be used only as fallback as it doesn't know
    about specific country holidays or extra working days.
    """
    # if the start date is on a weekend, forward the date to next Monday

    if start_date.weekday() > WEEKDAY_FRIDAY:
        start_date = start_date + timedelta(days=7 - start_date.weekday())

    # if the end date is on a weekend, rewind the date to the previous Friday
    if end_date.weekday() > WEEKDAY_FRIDAY:
        end_date = end_date - timedelta(days=end_date.weekday() - WEEKDAY_FRIDAY)

    if start_date > end_date:
        return 0
    # that makes the difference easy, no remainders etc
    diff_days = (end_date - start_date).days + 1
    weeks = int(diff_days / 7)

    remainder = end_date.weekday() - start_date.weekday() + 1

    if remainder != 0 and end_date.weekday() < start_date.weekday():
        remainder = 5 + remainder

    return weeks * 5 + remainder


def get_next_work_day(date: date):
    if date.weekday() == 4:
        return date + timedelta(days=3)
    elif date.weekday == 5:
        return date + timedelta(days=2)
    else:
        return date + timedelta(days=1)
