DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS investment;
DROP TABLE IF EXISTS portfolio;

CREATE TABLE user (
  username TEXT PRIMARY KEY UNIQUE NOT NULL
);

CREATE TABLE investment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  portfolio TEXT NOT NULL,
  duration REAL NOT NULL,
  principal REAL NOT NULL,
  FOREIGN KEY (username) REFERENCES user (username),
  FOREIGN KEY (portfolio) REFERENCES portfolio (id)
);

CREATE TABLE portfolio (
    id TEXT PRIMARY KEY UNIQUE NOT NULL,
    max REAL NOT NULL,
    min REAL NOT NULL,
    risk INT NOT NULL
);

INSERT INTO portfolio (id, max, min, risk)
VALUES
    ("A", 0.02, 0.01, 1),
    ("B", 0.05, -0.005, 3),
    ("C", 0.045, 0, 2);