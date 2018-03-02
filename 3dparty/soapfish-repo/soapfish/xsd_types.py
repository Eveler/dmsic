# -*- coding: utf-8 -*-
"""
Python class to map data types from XSD schema as accurately as possible.
We need to define custom data types because built-in Python types sometimes
don't match definitions for XSD.

For example xsd.Date might contain a timezone reference but that is not allowed
for datetime.date.
"""

from __future__ import absolute_import

from datetime import date


class XSDDate(object):
    """
    Represents the value of a xsd.date. Please note that dates in an XML schema
    can have time zone information attached (unlike Python's datetime.date).
    Also the schema spec supports "negative" dates (B.C.) and dates with
    years > 10000.

    Currently this class only supports dates representable by Python's
    datetime.date (with an optional time zone attached) but you should not
    assume that this will be true forever (see LIMITATIONS.md for further
    information).
    """
    def __init__(self, year, month, day, tzinfo=None):
        self.year = year
        self.month = month
        self.day = day
        self.tzinfo = tzinfo
        # simplistic validation that the provided date is actually valid
        self.as_datetime_date()

    @classmethod
    def from_datetime_date(cls, dt_date):
        return XSDDate(dt_date.year, dt_date.month, dt_date.day, tzinfo=None)

    def strftime(self, format_):
        """
        The usual strftime as implemented on datetime.date (thus without time
        zone support).
        As this method currently does not support time zones it should be
        used with care and probably treated as INTERNAL API.
        """
        return self.as_datetime_date().strftime(format_)

    def as_datetime_date(self):
        """
        Return a datetime.date instance which represents the same date as this
        instance (silently ignores the time zone information if present).
        Raises a ValueError if the date is not representable by datetime.date.
        """
        return date(self.year, self.month, self.day)

    def __eq__(self, other):
        attrs = ('year', 'month', 'day', 'tzinfo')
        for key in attrs:
            if not hasattr(other, key):
                return False
            self_value = getattr(self, key)
            other_value = getattr(other, key)
            if self_value != other_value:
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return 'XSDDate(%r, %r, %r, tzinfo=%r)' % (self.year, self.month, self.day, self.tzinfo)
