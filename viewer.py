#!/usr/bin/python3 -b

import os
import sqlite3
import traceback
import unicodedata

from flask import Flask, g, render_template, request, url_for

from auth import User, handle_login, handle_logout, login_required


def default_config():
  return dict(
    SECRET_KEY=os.urandom(128),
    DEBUG=True
  )


app = Flask(__name__)
app.config.update(default_config())
app.config.from_pyfile('config.py')
app.config['USERS'] = { x[0]: User(*x) for x in app.config['USERS'] }


def connect_db():
  db = sqlite3.connect(app.config['DB_PATH'])
# FIXME: Python 3.4
#  db = sqlite3.connect(
#    'file:/%s?mode=ro'.format(app.config['DB_PATH']), uri=True
#  )
  db.row_factory = sqlite3.Row
  return db


def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = g._database = connect_db()
  return db


@app.teardown_appcontext
def close_db(exception):
  db = getattr(g, '_database', None)
  if db is not None:
    db.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
  return handle_login(lambda x: None, 'cnf_index')


@app.route('/logout')
@login_required
def logout():
  return handle_logout(lambda x: None)


@app.route('/')
@login_required
def front():
  return render_template(
    'front.html',
    year=app.config['EDITION_YEAR'],
    number=app.config['EDITION_NUMBER']
  )


@app.route('/about')
@login_required
def about():
  return render_template('about.html', year=app.config['EDITION_YEAR'])


@app.route('/guide')
@login_required
def guide():
  return render_template('guide.html', year=app.config['EDITION_YEAR'])


@app.route('/media')
@login_required
def media():
  return render_template('media.html', year=app.config['EDITION_YEAR'])


@app.route('/archives')
@login_required
def archives():
  return render_template('archives.html', year=app.config['EDITION_YEAR'])


@app.route('/contact')
@login_required
def contact():
  return render_template('contact.html', year=app.config['EDITION_YEAR'])


#@app.route('/donate')
#@login_required
#def media():
#  return render_template('media.html')


@app.route('/colophon')
@login_required
def colophon():
  return render_template('colophon.html', year=app.config['EDITION_YEAR'])


def strip_marks(s):
  return ''.join(
    c for c in unicodedata.normalize('NFKD', s)
    if unicodedata.category(c)[0] != 'M'
  )


@app.route('/names', methods=['GET'])
@login_required
def cnf_index():
  c = get_db().cursor()

  # get CNFs
  c.execute('SELECT nym, live FROM cnf')
  rows = c.fetchall()

  # index by initial letter
  index = {}
  for row in rows:
    n = row['nym']
    f = unicodedata.normalize('NFKD', n[0])[0]
    index.setdefault(f, []).append((n, bool(row['live'])))
  index = sorted(index.items())

  # sort each letter by nym, stripped of diacritical marks
  for _, nl in index:
    nl.sort(key=lambda x: strip_marks(x[0]))

  return render_template(
    'cnf_index.html',
    index=index,
    year=app.config['EDITION_YEAR']
  )


def get_authors(table, id):
  c = get_db().cursor()
  c.execute('SELECT authors.skey, authors.prenames_short, authors.surname FROM {0} INNER JOIN authors ON {0}.author = authors.id WHERE {0}.ref=?'.format(table), (id,))
  return set(
    (r['skey'], '{} {}'.format(r['prenames_short'], r['surname']))
    for r in c.fetchall()
  )


@app.route('/name/<nym>', methods=['GET'])
@login_required
def cnf(nym):
  c = get_db().cursor()

  # get CNF
  c.execute('SELECT * FROM cnf WHERE nym = ? COLLATE NOCASE LIMIT 1', (nym,))
  cnf = c.fetchone()

  if cnf is None:
    return render_template(
      'missing.html',
      entry=nym,
      year=app.config['EDITION_YEAR']
    )

  authors = get_authors('cnf_authors', cnf['id'])

  # get VNFs
  order = ['area', 'lang', 'dim', 'date', 'name', 'case', 'key', 'bib_loc']

  # set the hierarchical order from the order query key
  qorder = request.args.get('order')
  if qorder:
    x = []
    for field in qorder.split(','):
      order.remove(field)
      x.append(field)
    x += order
    order = x

  # determine key index, and whether key and loc are adjacent
  key_loc_index = len(order)
  for i in range(len(order)):
    if order[i] == 'key':
      key_index = i
      if i != len(order)-1 and order[i+1] == 'bib_loc':
        key_loc_index = i
      break
    if order[i] == 'bib_loc':
      if i != len(order)-1 and order[i+1] == 'key':
        key_index = i+1
        key_loc_index = i
        break

  prevcite = None

  def ibid_func(v):
    return '<span class="bib_key">' + ('ibid.' if v == prevcite else v) + '</span>'

  funcs = {
    'area'    : lambda v: '<span class="area">' + v + '</span>',
    'lang'    : lambda v: '<span class="lang">' + v + '</span>',
    'dim'     : lambda v: '<span class="dim">' + ('◑' if v else '●') + '</span>',
    'date'    : lambda v: '<span class="date">' + v + '</span>',
    'name'    : lambda v: '<span class="name">' + v + '</span>',
    'case'    : lambda v: '(<span class="case">' + v + '</span>)' if v != 'n/a' else '',
    'key'     : ibid_func,
    'bib_loc' : lambda v: '<span class="bib_loc">' + v + '</span>' if v else ''
  }

  selectcols = ', '.join(list('"{}"'.format(x) for x in order) + ['vnf.id', 'vnf.live'])
  sortcols = selectcols.replace('area', 'area_skey', 1).replace('lang', 'lang_skey', 1).replace('date', 'date_skey', 1)
  sql = 'SELECT {} FROM vnf INNER JOIN vnf_cnf ON vnf.id = vnf_cnf.vnf INNER JOIN bib ON vnf.bib_id = bib.id WHERE cnf = ? ORDER BY {}'.format(selectcols, sortcols)

  vnfhtml = empty_vnfhtml = '<dl>\n'
  prev = [False] * len(order)

  for vnf in c.execute(sql, (cnf['id'],)):
    authors |= get_authors('vnf_authors', vnf['id'])

#    print(tuple(vnf[n] for n in range(len(vnf))), file=sys.stderr)

    for i in range(len(order)):
      if prev[i] != vnf[order[i]]:
        # ibid, but only within the flat part
        prevcite = prev[key_index] if i > 2 else None

        # close hierarchical parts
        if i <= 2:
          if prev[0]:
            vnfhtml += '</dd>\n'
            if i == 0:
              vnfhtml += '</dl>\n</dd>\n'
        # end top level of flat part with semicolon
        elif i == 3:
          vnfhtml += ';\n'
        # end other entries of flat part with comma
        else:
          vnfhtml += ',\n'

        # elements differing from previous entry
        for k in range(i, len(order)):
          prev[k] = vnf[order[k]]
          ehtml = funcs[order[k]](prev[k])

          # open hierarchical parts
          if k == 0:
            vnfhtml += '<dt>'
          elif k == 1:
            vnfhtml += '<dt>'
          elif k == 2:
            vnfhtml += '<dd>'
          # spacing for flat parts
          elif ehtml:
            vnfhtml += ' '

          # open link for adjacent key and location
          if k == key_loc_index:
            vnfhtml += '<a {}href="{}">'.format(
              'class="todo" ' if not vnf['live'] else '',
              url_for(
                'vnf', name=vnf['name'],
                date=vnf['date'].replace('/', 's'),
                bibkey=vnf['key']
              )
            )

          vnfhtml += ehtml

          # close link for adjacent key and location
          if k == key_loc_index + 1:
            vnfhtml += '</a>'

          # open hierarchical parts
          if k == 0:
            vnfhtml += '</dt>\n<dd>\n<dl>\n'
          elif k == 1:
            vnfhtml += '</dt>\n'

        break

  if vnfhtml != empty_vnfhtml:
    vnfhtml += '</dd>\n</dl>\n</dd>\n</dl>'
  else:
    vnfhtml = None

  authors = ', '.join(a[1] for a in sorted(authors))

  return render_template(
    'cnf.html',
    cnf=cnf,
    vnfhtml=vnfhtml,
    authors=authors,
    year=app.config['EDITION_YEAR'],
    number=app.config['EDITION_NUMBER'],
    preview=app.config['PREVIEW']
  )


@app.route('/cite/<name>/<date>/<bibkey>', methods=['GET'])
@login_required
def vnf(name, date, bibkey):
  c = get_db().cursor()

  sdate = date.replace('s', '/')

  # get VNF
  c.execute('SELECT * FROM vnf INNER JOIN bib ON vnf.bib_id = bib.id WHERE name = ? AND date = ? AND key = ? LIMIT 1', (name, sdate, bibkey))
  vnf = c.fetchone()

  if vnf is None:
    return render_template(
      'missing.html',
      entry='{}/{}/{}'.format(name, date, bibkey),
      year=app.config['EDITION_YEAR']
    )

  # get CNFs
  c.execute('SELECT nym FROM cnf INNER JOIN vnf_cnf ON cnf.id = vnf_cnf.cnf WHERE vnf_cnf.vnf = ?', (vnf['id'],))
  cnfs = c.fetchall()

  return render_template(
    'vnf.html',
    vnf=vnf,
    cnfs=cnfs,
    year=app.config['EDITION_YEAR']
  )


@app.route('/bibs', methods=['GET'])
@login_required
def bib_index():
  c = get_db().cursor()

  # get bibs
  c.execute('SELECT * FROM bib')
  bibs = c.fetchall()

  # sort by keys, stripped of diacritical marks
  bibs = list(bibs)
  bibs.sort(key=lambda x: strip_marks(x['key']))

  return render_template(
    'bib_index.html',
    bibs=bibs,
    year=app.config['EDITION_YEAR']
  )


@app.route('/bib/<key>', methods=['GET'])
@login_required
def bib(key):
  c = get_db().cursor()

  # get bib entry
  c.execute('SELECT * FROM bib WHERE key = ? LIMIT 1', (key,))
  b = c.fetchone()

  if b is None:
    return render_template(
      'missing.html',
      entry=key,
      year=app.config['EDITION_YEAR']
    )

  # get VNFs for bib
  c.execute('SELECT name, date FROM vnf WHERE bib_id = ?', (b['id'],))
  vnfs = c.fetchall()

  # sort VNFs by name, stripped of diacritical marks
  vnfs = list(vnfs)
  vnfs.sort(key=lambda x: strip_marks(x['name']))

  return render_template(
    'bib.html',
    bib=b,
    vnfs=vnfs,
    year=app.config['EDITION_YEAR']
  )

@app.errorhandler(404)
def handle_404(ex):
    return render_template('404.html'), 404

@app.errorhandler(Exception)
def handle_exception(ex):
  ex_text = traceback.format_exc()
  return render_template(
    'exception.html',
    ex=ex_text,
    year=app.config['EDITION_YEAR']
  ), 500


if __name__ == '__main__':
  app.run()
