# -*- coding: utf-8 -*-
import re
from lxml.objectify import ObjectifiedElement
import lxml.etree as etree

def convert_camel_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def pythonize(obj, is_list=False):
    for k, v in obj.__dict__.items():
        # obj.AttrTest = 3
        # => obj.attr_test = 3
        if k == 'xml':
            continue
        if isinstance(getattr(obj, k), ObjectifiedElement):
            if len(v) <= 1:
                v = pythonize(v)
            else:
                is_list = True
                l = []
                for e in v:
                    l.append(pythonize(e))
                    delattr(obj, k)
                v = l
        # If not a list of elements, set new attribute and delete old one
        setattr(obj, convert_camel_case(k), v)
        if not is_list:
            delattr(obj, k)
    return obj


def pretty_xml(xml):
    s = etree.fromstring(xml)
    return etree.tostring(s, pretty_print=True)
