from datetime import date
from calendar import isleap
from typing import Optional


def date_has_passed(date_of_birth: date, at_date: date) -> bool:
    return (at_date.month, at_date.day) >= (date_of_birth.month, date_of_birth.day)


def get_age(
    date_of_birth: Optional[date] = None, at_date: Optional[date] = None
) -> Optional[int]:
    if not date_of_birth:
        return None

    at_date = at_date or date.today()
    return (
        at_date.year
        - date_of_birth.year
        - (not date_has_passed(date_of_birth, at_date))
    )


def get_next_birthday(
    date_of_birth: Optional[date] = None, at_date: Optional[date] = None
) -> Optional[date]:
    if not date_of_birth:
        return None

    at_date = at_date or date.today()
    year = at_date.year

    if date_has_passed(date_of_birth, at_date):
        year += 1

    if date_of_birth.month == 2 and date_of_birth.day == 29 and not isleap(year):
        return date(year, 3, 1)

    return date(year, date_of_birth.month, date_of_birth.day)


def next_birthday_is_decadal(age: Optional[int] = None) -> bool:
    age = age or 0
    return (age + 1) % 10 == 0
