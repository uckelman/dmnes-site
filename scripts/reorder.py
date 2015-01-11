#!/usr/bin/python3 -b

import lxml.etree
import sys

def order(x):
  return {
    'name':  0,
    'meta':  1,
    'nym':   2,
    'gen':   3,
    'case':  4,
    'dim':   5,
    'lang':  6,
    'place': 7,
    'date':  8,
    'bibl':  9,
    'note': 10
  }[x.tag]

for filename in sys.argv[1:]:
  with open(filename) as f:
    doc = lxml.etree.parse(f)
  root = doc.getroot()
  root[:] = sorted(root, key=order)

  with open(filename, 'wb') as f:
    doc.write(
      f,
      xml_declaration='<?xml version="1.0" encoding="UTF-8"?>',
      encoding='UTF-8',
      pretty_print=False
    )
