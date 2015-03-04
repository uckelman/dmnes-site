import itertools
import lxml.etree
import lxml.objectify


def make_db_handle(db):
  dbh = db.cursor()
  dbh.execute("PRAGMA foreign_keys = ON")
  return dbh


def str_inner(node):
  return ''.join([node.text or ''] + list(lxml.etree.tostring(c, encoding='unicode') for c in node.getchildren()) + [node.tail or ''])


def make_parser():
  return lxml.objectify.makeparser()


def make_validating_parser(filename):
  with open(filename) as f:
    doc = lxml.etree.parse(f)

  schema = lxml.etree.XMLSchema(doc)
  return lxml.objectify.makeparser(schema=schema, remove_blank_text=False)


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


def make_span_xslt():
  xslt_root = lxml.etree.XML(b'''\
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes" encoding="UTF-8"/>

  <!-- identity transformation -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- elements not appearing in HTML5 become spans -->
  <xsl:template match="*[not(
       name() = 'a'
    or name() = 'abbr'
    or name() = 'address'
    or name() = 'area'
    or name() = 'article'
    or name() = 'aside'
    or name() = 'audio'
    or name() = 'b'
    or name() = 'base'
    or name() = 'bdi'
    or name() = 'bdo'
    or name() = 'blockquote'
    or name() = 'body'
    or name() = 'br'
    or name() = 'button'
    or name() = 'canvas'
    or name() = 'caption'
    or name() = 'cite'
    or name() = 'code'
    or name() = 'col'
    or name() = 'colgroup'
    or name() = 'data'
    or name() = 'datalist'
    or name() = 'dd'
    or name() = 'del'
    or name() = 'dfn'
    or name() = 'div'
    or name() = 'dl'
    or name() = 'dt'
    or name() = 'em'
    or name() = 'embed'
    or name() = 'fieldset'
    or name() = 'figcaption'
    or name() = 'figure'
    or name() = 'footer'
    or name() = 'form'
    or name() = 'h1'
    or name() = 'h2'
    or name() = 'h3'
    or name() = 'h4'
    or name() = 'h5'
    or name() = 'h6'
    or name() = 'head'
    or name() = 'header'
    or name() = 'hr'
    or name() = 'html'
    or name() = 'i'
    or name() = 'iframe'
    or name() = 'img'
    or name() = 'input'
    or name() = 'ins'
    or name() = 'kbd'
    or name() = 'keygen'
    or name() = 'label'
    or name() = 'legend'
    or name() = 'li'
    or name() = 'link'
    or name() = 'main'
    or name() = 'map'
    or name() = 'mark'
    or name() = 'meta'
    or name() = 'meter'
    or name() = 'nav'
    or name() = 'noscript'
    or name() = 'object'
    or name() = 'ol'
    or name() = 'optgroup'
    or name() = 'option'
    or name() = 'output'
    or name() = 'p'
    or name() = 'param'
    or name() = 'pre'
    or name() = 'progress'
    or name() = 'q'
    or name() = 'rb'
    or name() = 'rp'
    or name() = 'rt'
    or name() = 'rtc'
    or name() = 'ruby'
    or name() = 's'
    or name() = 'samp'
    or name() = 'script'
    or name() = 'section'
    or name() = 'select'
    or name() = 'small'
    or name() = 'source'
    or name() = 'span'
    or name() = 'strong'
    or name() = 'style'
    or name() = 'sub'
    or name() = 'sup'
    or name() = 'table'
    or name() = 'tbody'
    or name() = 'td'
    or name() = 'template'
    or name() = 'textarea'
    or name() = 'tfoot'
    or name() = 'th'
    or name() = 'thead'
    or name() = 'time'
    or name() = 'title'
    or name() = 'tr'
    or name() = 'track'
    or name() = 'u'
    or name() = 'ul'
    or name() = 'var'
    or name() = 'video'
    or name() = 'wbr'
  )]">
    <span class="{name()}"><xsl:apply-templates select="@*|node()"/></span>
  </xsl:template>
</xsl:stylesheet>
''')
  return lxml.etree.XSLT(xslt_root)
