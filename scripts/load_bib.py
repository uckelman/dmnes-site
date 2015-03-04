#!/usr/bin/python3 -b

import sqlite3
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

  # connect to the database
  with sqlite3.connect(sys.argv[1]) as db:
    dbh = make_db_handle(db)

    # process each bib file
    for filename in sys.argv[2:]:
      try:
        process_bib(parser, dbh, filename)
      except Exception as e:
        print(filename, e, file=sys.stderr)


if __name__ == '__main__':
  main()
