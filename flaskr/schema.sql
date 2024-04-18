DROP TABLE IF EXISTS gongjian;
DROP TABLE IF EXISTS StandardParameters;
DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS post;

CREATE TABLE gongjian (
  id_g INTEGER PRIMARY KEY AUTOINCREMENT,
  huahen INTEGER NOT NULL,
  angle FLOAT NOT NULL,
  circle INTEGER NOT NULL,
  lenth FLOAT NOT NULL,
  hege INTEGER NOT NULL,
  address TEXT NOT NULL,
  created datetime NOT NULL,
  standardid INTEGER,
  FOREIGN KEY (standardid) REFERENCES StandardParameters(standardid)
);

CREATE TABLE StandardParameters(
  standardid INTEGER PRIMARY KEY AUTOINCREMENT,
  length FLOAT NOT NULL,
  lengthError FLOAT NOT NULL,
  circles INTEGER NOT NULL,
  angleParam FLOAT NOT NULL,
  angleError FLOAT NOT NULL
);


CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  phone char(11) NOT NULL,
  status INTEGER NOT NULL DEFAULT 0,
  created_at datetime DEFAULT CURRENT_TIMESTAMP
);

-- CREATE TABLE post (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   author_id INTEGER NOT NULL,
--   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   title TEXT NOT NULL,
--   body TEXT NOT NULL,
--   FOREIGN KEY (author_id) REFERENCES user (id)
-- );