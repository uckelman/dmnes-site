#!/usr/bin/python3 -b

import lxml.etree;
import sqlite3
import sys

from dmnes import *


def make_cnf_row(cnf):
  return (
    str(cnf.nym),
    str(cnf.gen),
    str_inner(cnf.etym),
    str_inner(cnf.usg) if hasattr(cnf, 'usg') else None,
    str_inner(cnf['def']) if hasattr(cnf, 'def') else None
  )


def insert_cnf(dbh, cnf):
  cnf_r = make_cnf_row(cnf)
  dbh.execute(
    "INSERT INTO cnf (nym, gen, etym, usg, def) VALUES (?,?,?,?,?)",
    cnf_r
  )
  return dbh.lastrowid


def process_cnf(parser, dbh, filename):
  cnf = parse_xml(parser, filename)
  cnf_id = insert_cnf(dbh, cnf)
  insert_notes(dbh, "cnf_notes", cnf_id, cnf)


def main():
  parser = make_validating_parser(sys.argv[2]) 

  # connect to the database
  with sqlite3.connect(sys.argv[1]) as db:
    dbh = db.cursor()
    dbh.execute("PRAGMA foreign_keys = ON")

    # process each CNF file
    for filename in sys.argv[3:]:
      try:
        process_cnf(parser, dbh, filename)
      except:
        print(filename, file=sys.stderr)
        raise

if __name__ == '__main__':
  main()
