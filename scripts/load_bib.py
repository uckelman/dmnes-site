#!/usr/bin/python3 -b

import sys

from dmnes import *


def make_bib_row(bib):
  # FIXME: this is ugly, ugly, ugly
  data = str_inner(bib)
  data = data[data.index('</key>')+6:]
  return (
    str(bib.key),
    data
  )


def insert_bib(dbh, bib):
  bib_r = make_bib_row(bib)
  dbh.execute(
    "INSERT INTO bib (key, data) VALUES (?, ?)",
    bib_r
  )


def process_bib(parser, trans, dbh, filename):
  bib = parse_xml(parser, filename)
  spanned_bib = trans(bib).getroot()
  insert_bib(dbh, spanned_bib)
  

def main():
  parser = make_parser()
  trans = make_xslt(sys.argv[2])
  xml_to_db(parser, trans, process_bib, sys.argv[1], sys.argv[3:])


if __name__ == '__main__':
  main()
