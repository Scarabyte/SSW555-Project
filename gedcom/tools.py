"""
Tools for gedcom project
"""
import re
from datetime import datetime

import parser

NOW = datetime.now()
NOW_STRING = NOW.strftime("%d %b %Y").upper()

# TODO: Better Comments


def parse_date(s):
    """
    parse linedate string into datetime object
    """
    for fmt in ('%d %b %Y', '%b %Y', '%Y'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise ValueError("Unsupported Date Format")


def days_between(a, b):
    """ Calculate the days between two dates

    :param a: datetime 1
    :param b: datetime 2

    :return: days between two dates
    :rtype: float

    """
    return abs((a - b).days)


def years_between(a, b):
    """ Calculate the years between two dates

    :param a: datetime 1
    :param b: datetime 2

    :return: years between two dates
    :rtype: float

    """
    return abs(round(float((a - b).days) / 365, 2))


def human_sort(s, _re=re.compile('([0-9]+)')):
    """
    key for natural sorting
    example: alist.sort(key=human_sort)    #sorts the list in place (returns none)
    example: sorted(alist, key=human_sort) #returns a new list
    """
    try:
        return [int(x) if x.isdigit() else x.lower() for x in re.split(_re, s)]
    except:
        return s
