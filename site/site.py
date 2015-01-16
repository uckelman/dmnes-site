#!/usr/bin/python3 -b

import os
import sqlite3
import sys
import traceback

from flask import Flask, g, render_template, request


app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
  DB_PATH='dmnes.sqlite',
  SECRET_KEY=os.urandom(128),
  DEBUG=True
))


def connect_db():
  db = sqlite3.connect(app.config['DB_PATH'])
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


@app.route('/')
def slash():
  return 'Welcome to the DMNES!'


def sortedtree(t):
  if not hasattr(t, 'keys') or type(t) is sqlite3.Row:
    return t

  for k in t.keys():
    t[k] = sortedtree(t[k])    
  return tuple(sorted(t.items()))


@app.route('/cnf', methods=['GET'])
def cnf_list():
  c = get_db().cursor()

  # get CNF
  c.execute('SELECT nym FROM cnf')
  nyms = c.fetchall()

  return render_template('cnf_list.html', nyms=nyms)


@app.route('/cnf/<nym>', methods=['GET'])
def cnf(nym):
  c = get_db().cursor()

  # get CNF
  c.execute('SELECT * FROM cnf WHERE nym = ? COLLATE NOCASE LIMIT 1', (nym,))
  cnf = c.fetchone()
# TODO: handle no result

  # get VNFs
  order = ('area', 'lang', 'dim', 'name', 'case', 'date', 'key', 'bib_loc')

  key_index = 6
  prevcite = None 

  def ibid_func(v):
    return '<key>' + ('ibid' if v == prevcite else v) + '</key>'

  funcs = (
    lambda v: '<area>' + v + '</area>',
    lambda v: '<lang>' + v + '</lang>',
    lambda v: '<dim>' + ('◑' if v else '●') + '</dim>',
    lambda v: '<name>' + v + '</name>',
    lambda v: '(<case>' + v + '</case>)',
    lambda v: '<date>' + v + '</date>',
    ibid_func,
    lambda v: '<bib_loc>' + v + '</bib_loc>'
  )

#  for vnf in c.execute('SELECT vnf.id, name, "case", dim, lang, area, date, key, bib_loc FROM vnf INNER JOIN vnf_cnf ON vnf.id = vnf_cnf.vnf INNER JOIN bib ON vnf.bib_id = bib.id WHERE cnf = ? ORDER BY ?,?,?,?,?,?,?', (cnf['id'],) + order):
#  for vnf in c.execute('SELECT name, "case", dim, lang, area, date, key, bib_loc FROM vnf INNER JOIN vnf_cnf ON vnf.id = vnf_cnf.vnf INNER JOIN bib ON vnf.bib_id = bib.id WHERE cnf = ?', (cnf['id'],)):

  qorder = ', '.join('"{}"'.format(x) for x in order)
  query = 'SELECT {} FROM vnf INNER JOIN vnf_cnf ON vnf.id = vnf_cnf.vnf INNER JOIN bib ON vnf.bib_id = bib.id WHERE cnf = ? ORDER BY {}'.format(qorder, qorder)

  tree = {}

  vnfxml = ''

  prev = [False] * len(order)

  for vnf in c.execute(query, (cnf['id'],)):
# TODO: handle date sorting
#    print(tuple(vnf[n] for n in range(len(vnf))), file=sys.stderr)

    for i in range(len(order)):
      if prev[i] != vnf[order[i]]:
        # ibid, but only within the flat part
        prevcite = prev[key_index] if i > 2 else None

        # close hierarchical parts
        if i <= 2:
          if prev[0]:
            print((' ' * i) + '</dd>')
            if i <= 1:
              print((' ' * i) + '</dl>')
              if i == 0:
                print((' ' * i) + '</dd>')
        # end top level of flat part with semicolon
        elif i == 3:
          print((' ' * i) + ';')
        # end other entries of flat part with comma
        elif i > 4:
          print((' ' * i) + ',')
         
        # elements differing from previous entry
        for k in range(i, len(order)):

          # open hierarchical parts
          if k == 0:
            print((' ' * k) + '<dt>')
          elif k == 1:
            print((' ' * k) + '<dt>')
          elif k == 2:
            print((' ' * k) + '<dd>')

          prev[k] = vnf[order[k]]
          print((' ' * k) + funcs[k](prev[k]))

          # open hierarchical parts
          if k == 0:
            print((' ' * k) + '</dt><dd><dl>')          
          elif k == 1:
            print((' ' * k) + '</dt>')

        break

    # create tree from VNFs

    x = tree
    for d in range(len(order)-1):
      if vnf[order[d]] not in x:
        x[vnf[order[d]]] = {}
      x = x[vnf[order[d]]] 
    x[vnf[order[len(order)-1]]] = True

  print('</dd></dl></dd>')

  tree = sortedtree(tree)
  return render_template('cnf.html', cnf=cnf, vnfs=tree, order=order)


@app.route('/vnf/<name>/<date>/<bibkey>', methods=['GET'])
def vnf(name, date, bibkey):
  c = get_db().cursor()

  # get VNF
  c.execute('SELECT * FROM vnf INNER JOIN bib ON vnf.bib_id = bib.id WHERE name = ? AND date = ? AND key = ? LIMIT 1', (name, date, bibkey))
  vnf = c.fetchone()

  # get CNFs
  c.execute('SELECT nym FROM cnf INNER JOIN vnf_cnf ON cnf.id = vnf_cnf.cnf WHERE vnf_cnf.vnf = ?', (vnf['id'],))
  cnfs = c.fetchall()

  return render_template('vnf.html', vnf=vnf, cnfs=cnfs)


@app.route('/bib/<key>', methods=['GET'])
def bib(key):
  c = get_db().cursor()

  # get bib entry
  c.execute('SELECT * FROM bib WHERE key = ? LIMIT 1', (key,))
  b = c.fetchone()

  return render_template('bib.html', bib=b)


@app.errorhandler(Exception)
def handle_exception(ex):
  ex_text = traceback.format_exc()
  return render_template('exception.html', ex=ex_text), 500


if __name__ == '__main__':
  app.run()
