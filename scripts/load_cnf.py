#!/usr/bin/python3 -b

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
  xml_to_db(parser, process_cnf, sys.argv[1], sys.argv[3:])


if __name__ == '__main__':
  main()
