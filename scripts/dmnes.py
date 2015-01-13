import itertools
import lxml.etree
import lxml.objectify


def str_inner(node):
  return ''.join([node.text or ''] + list(lxml.etree.tostring(c, encoding='unicode') for c in node.getchildren()) + [node.tail or ''])


def make_parser():
  return lxml.objectify.makeparser()


def make_validating_parser(filename):
  with open(filename) as f:
    doc = lxml.etree.parse(f)

  schema = lxml.etree.XMLSchema(doc)
  return lxml.objectify.makeparser(schema=schema)


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
