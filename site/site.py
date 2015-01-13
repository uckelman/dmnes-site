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
  if type(t) is list:
    for i in range(0, len(t)):
      t[i] = sortedtree(t[i])
    return tuple(t)

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
  order = ('area', 'lang', 'dim', 'name', 'date', 'key', 'bib_loc')

  c.execute('SELECT vnf.id, name, "case", dim, lang, area, date, key, bib_loc FROM vnf INNER JOIN vnf_cnf ON vnf.id = vnf_cnf.vnf INNER JOIN bib ON vnf.bib_id = bib.id WHERE cnf = ? ORDER BY ?,?,?,?,?,?,?', (cnf['id'],) + order)
  vnfs = c.fetchall()

  # create tree from VNFs
  vnf_tree = {}
  for vnf in vnfs:
    # extract the country
# TODO: handle date sorting

    area = vnf['area']
    lang = vnf['lang']
    name = vnf['name']
    dim = vnf['dim']

    if area not in vnf_tree:
      vnf_tree[area] = {}

    if lang not in vnf_tree[area]:
      vnf_tree[area][lang] = [{}, {}]

    if name not in vnf_tree[area][lang][dim]:
      vnf_tree[area][lang][dim][name] = []

    vnf_tree[area][lang][dim][name].append(vnf)

  vnf_tree = sortedtree(vnf_tree) 
  return render_template('cnf.html', cnf=cnf, vnfs=vnf_tree)


  




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
