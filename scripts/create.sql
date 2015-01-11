PRAGMA foreign_keys = ON;

CREATE TABLE cnf(
  id INTEGER PRIMARY KEY,
  nym TEXT UNIQUE NOT NULL,
  gen TEXT CHECK(gen IN ('M', 'F', 'U')) NOT NULL,
  etym TEXT,
  usg TEXT,
  def TEXT
);

CREATE TABLE cnf_notes(
  ref INTEGER NOT NULL REFERENCES cnf(id),
  note TEXT
);

CREATE INDEX cnf_notes_index ON cnf_notes(ref);

CREATE TABLE vnf(
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  gen TEXT CHECK(gen IN ('M', 'F', 'U')) NOT NULL,
  "case" TEXT CHECK("case" IN ('n/a', 'abl', 'acc', 'dat', 'gen', 'nom', 'obl', 'unc')) NOT NULL,
  dim INTEGER CHECK(dim == 0 OR dim == 1) NOT NULL,
  lang TEXT CHECK(LENGTH(lang) > 0) NOT NULL,
  place TEXT,
  date TEXT CHECK(LENGTH(date) > 0) NOT NULL,
  bib_id INTEGER NOT NULL REFERENCES bib(id),
  bib_loc TEXT
);

CREATE TABLE vnf_cnf(
  vnf INTEGER NOT NULL REFERENCES vnf(id),
  cnf INTEGER NOT NULL REFERENCES cnf(id)
);

CREATE INDEX vnf_cnf_index ON vnf_cnf(vnf);
CREATE INDEX cnf_vnf_index ON vnf_cnf(cnf);

CREATE TABLE vnf_notes(
  ref INTEGER NOT NULL REFERENCES vnf(id),
  note TEXT
);

CREATE INDEX vnf_notes_index ON vnf_notes(ref);

CREATE TABLE bib(
  id INTEGER PRIMARY KEY,
  key TEXT UNIQUE NOT NULL,
  data TEXT NOT NULL
);
