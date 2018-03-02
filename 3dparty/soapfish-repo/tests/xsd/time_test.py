# -*- coding: utf-8 -*-

from datetime import time

import iso8601
from lxml import etree
from pythonic_testcase import assert_equals, assert_raises

from soapfish import xsd
from soapfish.testutil import SimpleTypeTestCase


class TimeTest(SimpleTypeTestCase):
    xsd_type = xsd.Time

    def test_can_render_python_time(self):
        time_ = time(23, 59, 59)
        xmlelement = etree.Element('foo')
        xsd.Element(self.xsd_type).render(xmlelement, 'bar', time_)
        xml = self._normalize(etree.tostring(xmlelement, pretty_print=True))
        assert_equals(b'<foo><bar>23:59:59</bar></foo>', xml)

    def test_rendering_timezones(self):
        time_ = time(10, 15, 20, tzinfo=iso8601.FixedOffset(1, 15, 'dummy zone'))
        rendered_xml = self.xsd_type().xmlvalue(time_)
        assert_equals('10:15:20+01:15', rendered_xml)

    def test_wrong_type(self):
        mixed = xsd.Element(self.xsd_type)
        xmlelement = etree.Element('foo')
        assert_raises(Exception, lambda: mixed.render(xmlelement, 'bar', 1))

    def test_parsing_utctimezone(self):
        class Test(xsd.ComplexType):
            time_ = xsd.Element(self.xsd_type, tagname='time')
        parsed = Test.parsexml('<root><time>00:19:00Z</time></root>')
        assert_equals(time(0, 19, 0, tzinfo=iso8601.UTC), parsed.time_)

    def test_parsing_timezone(self):
        class Test(xsd.ComplexType):
            time_ = xsd.Element(self.xsd_type, tagname='time')
        parsed = Test.parsexml('<root><time>20:19:00+01:00</time></root>')
        assert_equals(time(20, 19, 0, tzinfo=iso8601.FixedOffset(1, 0, '+01:00')), parsed.time_)

    def test_accepts_only_compatible_types(self):
        self.assert_can_set(None)
        self.assert_can_set(time(23, 59, 59))

        self.assert_can_not_set(0)
        self.assert_can_not_set([])
        self.assert_can_not_set('invalid')

    def test_parsing(self):
        self.assert_parse(None, None)
        self.assert_parse(None, 'nil')
        parsed_time = self._parse('23:59:59+01:00')
        assert_equals(time(23, 59, 59, tzinfo=iso8601.FixedOffset(1, 0, '+01:00')), parsed_time)
        parsed_time = self._parse('23:59:59-02:30')
        assert_equals(time(23, 59, 59, tzinfo=iso8601.FixedOffset(-2, -30, '-02:30')), parsed_time)
