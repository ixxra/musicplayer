CREATE TABLE IF NOT EXISTS files(uri TEXT unique on conflict ignore);

CREATE TABLE IF NOT EXISTS tags(key TEXT, value TEXT, file_id REFERENCES files(rowid));

CREATE TABLE IF NOT EXISTS play_info(timesplayed integer, lastplayed date, loved boolean, file_id REFERENCES files(rowid));
