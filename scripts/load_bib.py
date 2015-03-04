#!/usr/bin/python3 -b

import sys

from dmnes import *


def make_bib_row(bib):
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


def process_bib(parser, dbh, filename):
  bib = parse_xml(parser, filename)
  insert_bib(dbh, bib)
  

def main():
  parser = make_parser()
  xml_to_db(parser, process_bib, sys.argv[1], sys.argv[2:])


if __name__ == '__main__':
  main()
