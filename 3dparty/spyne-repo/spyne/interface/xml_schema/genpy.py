
#
# spyne - Copyright (C) Spyne contributors.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#

"""
A barely functional Spyne class serializer. If you're using this as part of
anything serious, you're insane.

TODO:
  - Customizations are not serialized.
"""

import logging
logger = logging.getLogger(__name__)

import spyne

from datetime import datetime
from itertools import chain
from collections import defaultdict

from spyne.model import SimpleModel
from spyne.model.complex import XmlModifier
from spyne.model.complex import ComplexModelBase


def gen_fn_from_tns(tns):
    return tns \
        .replace('http://', '') \
        .replace('https://', '') \
        .replace('/', '') \
        .replace('.', '_') \
        .replace(':', '_') \
        .replace('#', '') \
        .replace('-', '_')


class CodeGenerator(object):
    def __init__(self, fn_tns_mapper=gen_fn_from_tns):
        self.imports = set()
        self.classes = set()
        self.pending = defaultdict(list)
        self.simples = set()
        self.fn_tns_mapper = fn_tns_mapper

    def gen_modifier(self, t):
        return '%s(%s)' % (t.__name__, self.gen_dispatch(t.type))

    def gen_simple(self, t):
        return t.__name__

    def gen_complex(self, t):
        retval = []
        retval.append("""

class %s(_ComplexBase):
    _type_info = [""" % (t.get_type_name()))

        for k,v in t._type_info.items():
            if not issubclass(v, ComplexModelBase) or \
                        v.get_namespace() != self.tns or \
                            v in self.classes or \
                                getattr(v, '__orig__', None) in self.classes:
                retval.append("        ('%s', %s)," % (k, self.gen_dispatch(v)))
            else:
                self.pending[v.get_type_name()].append((k, t.get_type_name()))

        retval.append("    ]")

        self.classes.add(t)

        for k,orig_t in self.pending[t.get_type_name()]:
            retval.append('%s._type_info["%s"] = %s' % (orig_t, k, t.get_type_name()))

        return retval

    def gen_dispatch(self, t):
        if issubclass(t, XmlModifier):
            return self.gen_modifier(t)

        if issubclass(t, SimpleModel):
            return self.gen_simple(t)

        if t.get_namespace() == self.tns:
            return t.get_type_name()

        i = self.fn_tns_mapper(t.get_namespace())
        self.imports.add(i)
        return "%s.%s" % (i, t.get_type_name())

    def genpy(self, tns, s):
        self.tns = tns

        retval = [u"""# encoding: utf8

# Automatically generated by Spyne %s at %s.
# Modify at your own risk.

from spyne.model import *
"""  % (spyne.__version__, datetime.now().replace(microsecond=0).isoformat(' ')),
"", # imports
"""

class _ComplexBase(ComplexModelBase):
    __namespace__ = '%s'
    __metaclass__ = ComplexModelMeta""" % tns
]

        for n, t in s.types.items():
            if issubclass(t, ComplexModelBase):
                retval.extend(self.gen_complex(t))
            else:
                retval.append('%s = %s' % (n, self.gen_dispatch(t)))
                self.simples.add(n)

        for i in self.imports:
            retval.insert(1, "import %s" % i)

        retval.append("")
        retval.append("")

        retval.append('__all__ = [')
        for c in sorted(chain([c.get_type_name() for c in self.classes],
                                                                self.simples)):
            retval.append("    '%s',"  % c)
        retval.append(']')
        retval.append("")

        return '\n'.join(retval)
