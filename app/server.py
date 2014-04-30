#!/usr/bin/python3 -b

import os
import subprocess
import unicodedata

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

import lxml
from lxml.builder import E

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
  REPO_DIR='dmnes',
  CNF_DIR='CNFs',
  VNF_DIR='VNFs',
  CNF_SCHEMA='../cnf.xsd',
  VNF_SCHEMA='../vnf.xsd',
  SECRET_KEY=os.urandom(128),
  DEBUG=True
))

accounts = {
  'uckelman': 'foobar',
}


#
# XML schemas
#

def load_schema(filename):
  with open(filename) as f:
    doc = lxml.etree.parse(f)

  return lxml.etree.XMLSchema(doc)


def get_cnf_schema():
  if not hasattr(g, 'cnf_schema'):
    g.cnf_schema = load_schema(app.config['CNF_SCHEMA'])
  return g.cnf_schema


def get_vnf_schema():
  if not hasattr(g, 'vnf_schema'):
    g.vnf_schema = load_schema(app.config['VNF_SCHEMA'])
  return g.vnf_schema


#
# Git functions
#

def do_git(repo_dir, cmd, *args):
  with subprocess.Popen(['git', cmd] + list(args), cwd=repo_dir) as proc:
    pass


#def git_clone(base_dir, repo_url, repo_dir):
#  do_git(base_dir, 'clone', repo_url, repo_dir)
#
#
#def git_checkout_branch(repo_dir, branch):
#  do_git(repo_dir, 'checkout', '-B', branch)


def git_add_file(repo_dir, path):
  do_git(repo_dir, 'add', path)


def git_commit_file(repo_dir, path):
  do_git(repo_dir, 'commit', '-m', 'Committed ' + path, path)


#
#
#

def prefix_branch(s, maxlen=3):
  return [s[n-1:n] for n in range(1,maxlen+1)] + [s]


def build_path(basedir, base):
  base = unicodedata.normalize('NFKC', base.lower())
  for evil in os.pardir, os.sep, os.altsep:
    if evil in base:
      raise RuntimeError('Evil path')
  return os.path.join(basedir, *prefix_branch(base)) + '.xml'


def cnf_path(cnf):
  return build_path(app.config['CNF_DIR'], cnf['nym'])


def vnf_path(vnf):
  return build_path(
    app.config['VNF_DIR'],
    '{}_{}_{}'.format(vnf['name'], vnf['date'], vnf['bib_key'])
  )


def xmlfrag(key, obj):
  return lxml.etree.fromstring('<{0}>{1}</{0}>'.format(key, obj[key]))


def build_cnf(cnf):
  root = E.cnf(
    E.nym(cnf['nym']),
    E.gen(cnf['gen']),
    xmlfrag('etym', cnf),
    xmlfrag('def', cnf),
    xmlfrag('usg', cnf),
    xmlfrag('note', cnf)
  ) 

  schema = get_cnf_schema()
  schema.assertValid(root)

  return lxml.etree.ElementTree(root)


def build_vnf(vnf):
  root = E.vnf(
    E.name(vnf['name']),
    E.nym(vnf['nym']),
    E.gen(vnf['gen']),
    E.case(vnf['case']),
    E.lang(vnf['lang']),
    xmlfrag('place', vnf),
    E.date(vnf['date']),
    E.bibl(
      E.key(vnf['bib_key']),
      E.loc(vnf['bib_loc'])
    ),
    xmlfrag('note', vnf)
  ) 

  schema = get_vnf_schema()
  schema.assertValid(root)

  return lxml.etree.ElementTree(root)


def write_tree(tree, path):
  os.makedirs(os.path.dirname(path), exist_ok=True)
  with open(path, 'wb') as f:
    tree.write(
      f,
      xml_declaration='<?xml version="1.0" encoding="UTF-8"?>',
      encoding='UTF-8',
      pretty_print=True
    )


def commit_to_git(tree, path):
  repo_dir = app.config['REPO_DIR']
  write_tree(tree, os.path.join(repo_dir, path))
  git_add_file(repo_dir, path)
  git_commit_file(repo_dir, path)


def add_cnf(cnf):
  tree = build_cnf(cnf)
  path = cnf_path(cnf)
  commit_to_git(tree, path)


def add_vnf(vnf):
  tree = build_vnf(vnf)
  path = vnf_path(vnf)
  commit_to_git(tree, path)


# TODO: checkout branch based on login
# TODO: store local repos per-user
# TODO: commit on logout?
# TODO: handle exceptions

#
# User authentication
#

def auth_user(username, password):
  if accounts.get(username, None) == password:
    return None
  return 'Invalid username or password!'


#
# URL handlers
#

@app.route('/')
def slash():
  return 'Welcome to the DMNES!'


@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    error = auth_user(username, password)
    if error == None:
      session['username'] = username
      flash('Welcome, ' + username + '.')
      return redirect(url_for('cnf'))

  return render_template('login.html', error=error)


@app.route('/logout')
def logout():
  session.pop('username', None)
  flash('Goodbye, ' + username + '.')
  return redirect(url_for(''))


@app.route('/cnf', methods=['GET', 'POST'])
def cnf():
  if 'username' not in session:
    abort(401)

  if request.method == 'POST':
    add_cnf(request.form)
    flash('Added ' + request.form['nym'])

  return render_template('cnf.html')


@app.route('/vnf', methods=['GET', 'POST'])
def vnf():
  if 'username' not in session:
    abort(401)

  if request.method == 'POST':
    add_vnf(request.form)
    flash('Added ' + request.form['name'])

    # retain some input values for next entry 
    keep = ('lang', 'place', 'date', 'bib_key')
    vals = {k: request.form[k] for k in keep}
  else:
    vals = {}

  return render_template('vnf.html', vals=vals)


if __name__ == '__main__':
  app.run()
