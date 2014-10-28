# -*- coding: utf-8 -*-
import re
from lxml.objectify import ObjectifiedElement
import lxml.etree as etree

def convert_camel_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def pythonize(obj, is_list=False):
    if hasattr(obj, '__keylist__'):
        res = {}
        for k, v in obj:
            if not hasattr(v, 'sort'): # not a list
                v = pythonize(v)
            else:
                is_list = True
                l = []
                for e in v:
                    l.append(pythonize(e))
                v = l
            res[convert_camel_case(k)] = pythonize(v)
        return res
    else:
        return obj

def pretty_xml(xml):
    s = etree.fromstring(xml)
    return etree.tostring(s, pretty_print=True)
