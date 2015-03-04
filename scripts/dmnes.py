import lxml.etree
import lxml.objectify
import sqlite3
import sys


def make_db_handle(db):
  dbh = db.cursor()
  dbh.execute("PRAGMA foreign_keys = ON")
  return dbh


def str_inner(node):
  return ''.join(
    [node.text or ''] +
    [lxml.etree.tostring(c, encoding='unicode') for c in node.getchildren()] +
    [node.tail or '']
  )


def make_parser():
  return lxml.objectify.makeparser()


def make_validating_parser(filename):
  with open(filename) as f:
    doc = lxml.etree.parse(f)

  schema = lxml.etree.XMLSchema(doc)
  return lxml.objectify.makeparser(schema=schema, remove_blank_text=False)


def make_xslt(filename):
  with open(filename) as f:
    doc = lxml.etree.parse(f)
  return lxml.etree.XSLT(doc)


def parse_xml(parser, filename):
  with open(filename) as f:
    tree = lxml.objectify.parse(f, parser=parser)
  return tree.getroot()


def make_note_rows(ref, obj):
  return tuple((ref, str_inner(n)) for n in obj.note)


def insert_notes(dbh, table, ref, obj):
  if hasattr(obj, 'note'):
    note_rs = make_note_rows(ref, obj)
    dbh.executemany(
      "INSERT INTO {} (ref, note) VALUES (?,?)".format(table),
      note_rs
    )


def xml_to_db(parser, trans, process, dbpath, xmlpaths):
  # connect to the database
  with sqlite3.connect(dbpath) as db:
    dbh = make_db_handle(db)

    # process each XML file
    for filename in xmlpaths:
      try:
        process(parser, trans, dbh, filename)
      except (lxml.etree.XMLSyntaxError, sqlite3.IntegrityError) as e:
        print(filename, e, file=sys.stderr)
