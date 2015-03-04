#!/usr/bin/bash -ex

rm -f dmnes.sqlite
sqlite3 dmnes.sqlite <create.sql

find ../site/dmnes/bib -type f -print0 | xargs -0 ./load_bib.py dmnes.sqlite span.xsl

find ../site/dmnes/CNFs -type f -print0 | xargs -0 ./load_cnf.py dmnes.sqlite ../site/dmnes/schemata/cnf.xsd span.xsl

find ../site/dmnes/VNFs -type f -print0 | xargs -0 ./load_vnf.py dmnes.sqlite ../site/dmnes/schemata/vnf.xsd span.xsl
